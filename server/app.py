"""
TeamEcho Flask 應用 - 使用 PostgreSQL 資料庫
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import uuid
import datetime
import traceback

# 導入資料庫相關模組
from models import db, User, UserToken, Form, Respondent, Feedback
from config import Config

def create_app():
    """創建 Flask 應用"""
    app = Flask(__name__)
    
    # 載入配置
    app.config.from_object(Config)
      # 驗證配置
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"配置錯誤: {e}")
        print("請檢查 .env 文件中的資料庫連接設定")
        return None
    
    # 初始化擴展
    CORS(app)
    db.init_app(app)
    
    # 在應用上下文中創建資料庫表
    with app.app_context():
        try:
            db.create_all()
            print("✅ 資料庫表格創建成功")
        except Exception as e:
            print(f"⚠️ 資料庫表格創建警告: {str(e)}")
    
    return app

app = create_app()

if app is None:
    exit(1)

# ----- Helpers -----
def generate_id():
    """生成唯一 ID"""
    return uuid.uuid4().hex

def generate_invite_code():
    """生成邀請碼"""
    return uuid.uuid4().hex[:6].upper()

def auth_required(f):
    """認證裝飾器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({
                'code': 'ACCESS_TOKEN_EXPIRED',
                'message': '訪問權杖已過期或無效'
            }), 401
        
        token = auth.split(' ', 1)[1]
        
        # 查詢資料庫中的 token
        user_token = UserToken.query.filter_by(token=token).first()
        if not user_token:
            return jsonify({
                'code': 'ACCESS_TOKEN_EXPIRED',
                'message': '訪問權杖已過期或無效'
            }), 401
        
        # 檢查 token 是否過期（如果設定了過期時間）
        if user_token.expires_at and user_token.expires_at < datetime.datetime.utcnow():
            db.session.delete(user_token)
            db.session.commit()
            return jsonify({
                'code': 'ACCESS_TOKEN_EXPIRED',
                'message': '訪問權杖已過期或無效'
            }), 401
        
        request.user_id = user_token.user_id
        request.user = user_token.user
        return f(*args, **kwargs)
    return wrapper

# ----- Routes -----
@app.route('/users', methods=['POST'])
def register_user():
    """用戶註冊"""
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # 檢查必要欄位
        if not all([name, email, password]):
            return jsonify({
                'code': 'MISSING_FIELDS',
                'message': '缺少必要欄位'
            }), 400
        
        # 檢查 email 是否已存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'code': 'EMAIL_CONFLICT',
                'message': '信箱已被註冊'
            }), 409
        
        # 創建新用戶
        user = User(
            name=name,
            email=email,
            password=password  # 在生產環境中應該加密密碼
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"註冊錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/sessions', methods=['POST'])
def login():
    """用戶登入"""
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')
        
        # 驗證用戶
        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            return jsonify({
                'code': 'WRONG_LOGIN',
                'message': '帳號密碼錯誤'
            }), 401
        
        # 生成新的 access token
        token = generate_id()
        user_token = UserToken(
            token=token,
            user_id=user.id
        )
        
        db.session.add(user_token)
        db.session.commit()
        
        return jsonify({
            'access_token': token,
            'token_type': 'bearer',
            'expires_in': 3600
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"登入錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/forms', methods=['POST'])
@auth_required
def create_form():
    """創建反饋表單"""
    try:
        data = request.get_json(force=True)
        title = data.get('title')
        respondents = data.get('respondents', [])
        
        # 檢查必要欄位
        if not title:
            return jsonify({
                'code': 'MISSING_FIELDS',
                'message': '缺少表單標題'
            }), 400
        
        # 檢查受邀者 email 是否重複
        emails = [r['email'] for r in respondents]
        if len(emails) != len(set(emails)):
            return jsonify({
                'code': 'RESPONDENT_DUPLICATE',
                'message': '受邀者 email 重複'
            }), 409
        
        # 創建表單
        form = Form(
            title=title,
            creator_id=request.user_id,
            invite_code=generate_invite_code()
        )
        
        db.session.add(form)
        db.session.flush()  # 取得 form.id
        
        # 添加受邀者
        for r in respondents:
            respondent = Respondent(
                form_id=form.id,
                name=r['name'],
                email=r['email']
            )
            db.session.add(respondent)
        
        db.session.commit()
        
        return jsonify({
            'form_id': form.id,
            'title': form.title,
            'invite_code': form.invite_code,
            'created_at': form.created_at.isoformat() + 'Z',
            'expire_at': None  # 可以後續添加過期功能
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"創建表單錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/forms', methods=['GET'])
@auth_required
def list_forms():
    """獲取用戶的表單列表"""
    try:
        forms = Form.query.filter_by(creator_id=request.user_id).all()
        
        result = []
        for form in forms:
            result.append({
                'form_id': form.id,
                'title': form.title,
                'invite_code': form.invite_code,
                'created_at': form.created_at.isoformat() + 'Z',
                'expire_at': None,
                'total_respondents': len(form.respondents),
                'total_responses': len(form.feedbacks)
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"獲取表單列表錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/forms/<invite_code>', methods=['GET'])
def get_form_by_invite(invite_code):
    """通過邀請碼獲取表單"""
    try:
        form = Form.query.filter_by(invite_code=invite_code).first()
        if not form:
            return jsonify({
                'code': 'FORM_NOT_FOUND',
                'message': '找不到對應的表單'
            }), 404
        
        return jsonify(form.to_dict())
        
    except Exception as e:
        print(f"獲取表單錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/forms/<invite_code>/feedback', methods=['POST'])
def submit_feedback(invite_code):
    """提交反饋"""
    try:
        form = Form.query.filter_by(invite_code=invite_code).first()
        if not form:
            return jsonify({
                'code': 'FORM_NOT_FOUND',
                'message': '找不到對應的表單'
            }), 404
        
        data = request.get_json(force=True)
        feedbacks = data.get('feedbacks', [])
        
        # 提交每個反饋
        for feedback_data in feedbacks:
            feedback = Feedback(
                form_id=form.id,
                respondent_name=feedback_data['respondent_name'],
                respondent_email=feedback_data['respondent_email'],
                feedback_text=feedback_data['feedback_content']
            )
            db.session.add(feedback)
        
        db.session.commit()
        
        return jsonify({'message': '反饋提交成功'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"提交反饋錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/forms/<form_id>/responses', methods=['GET'])
@auth_required
def get_form_responses(form_id):
    """獲取表單的所有回應"""
    try:
        form = Form.query.filter_by(id=form_id, creator_id=request.user_id).first()
        if not form:
            return jsonify({
                'code': 'FORM_NOT_FOUND',
                'message': '找不到對應的表單'
            }), 404
        
        responses = []
        for i, feedback in enumerate(form.feedbacks):
            responses.append({
                'response_id': i,
                'respondent_name': feedback.respondent_name,
                'respondent_email': feedback.respondent_email,
                'feedback_content': feedback.feedback_text,
                'created_at': feedback.created_at.isoformat() + 'Z' if feedback.created_at else None
            })
        
        return jsonify(responses)
        
    except Exception as e:
        print(f"獲取表單回應錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

@app.route('/forms/<form_id>/results', methods=['GET'])
@auth_required
def generate_results(form_id):
    """生成結果頁面（實際應用中可能需要 AI 分析）"""
    try:
        form = Form.query.filter_by(id=form_id, creator_id=request.user_id).first()
        if not form:
            return jsonify({
                'code': 'FORM_NOT_FOUND',
                'message': '找不到對應的表單'
            }), 404
        
        # 簡單的結果分析
        total_responses = len(form.feedbacks)
        
        return jsonify({
            'form_title': form.title,
            'total_responses': total_responses,
            'analysis': f'共收到 {total_responses} 份反饋',
            'created_at': form.created_at.isoformat() + 'Z'
        })
        
    except Exception as e:
        print(f"生成結果錯誤: {traceback.format_exc()}")
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': '內部伺服器錯誤'
        }), 500

# 健康檢查端點
@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    try:
        # 測試資料庫連接
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'        }), 500

if __name__ == '__main__':
    # 在生產環境中使用環境變數中的端口
    import os
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
