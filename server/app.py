from flask import Flask, request, jsonify
from functools import wraps
import uuid
import datetime

app = Flask(__name__)

# ----- In-memory storage -----
users = {}
# email -> uniq_id
email_index = {}
tokens = {}

forms = {}
# invite code -> form_id
invite_map = {}

# ----- Helpers -----
def generate_id():
    return uuid.uuid4().hex


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'code': 'ACCESS_TOKEN_EXPIRED',
                            'message': '訪問權杖已過期或無效'}), 401
        token = auth.split(' ', 1)[1]
        user_id = tokens.get(token)
        if not user_id:
            return jsonify({'code': 'ACCESS_TOKEN_EXPIRED',
                            'message': '訪問權杖已過期或無效'}), 401
        request.user_id = user_id
        return f(*args, **kwargs)
    return wrapper

# ----- Routes -----
@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json(force=True)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if email in email_index:
        return jsonify({'code': 'EMAIL_CONFLICT', 'message': '信箱已被註冊'}), 409
    user_id = generate_id()
    users[user_id] = {
        'uniq_id': user_id,
        'name': name,
        'email': email,
        'password': password  # plaintext for demo
    }
    email_index[email] = user_id
    return jsonify({'uniq_id': user_id, 'name': name, 'email': email}), 201


@app.route('/sessions', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email = data.get('email')
    password = data.get('password')
    user_id = email_index.get(email)
    if not user_id or users[user_id]['password'] != password:
        return jsonify({'code': 'WRONG_LOGIN', 'message': '帳號密碼錯誤'}), 401
    token = generate_id()
    tokens[token] = user_id
    return jsonify({'access_token': token, 'token_type': 'bearer', 'expires_in': 3600})


@app.route('/forms', methods=['POST'])
@auth_required
def create_form():
    data = request.get_json(force=True)
    title = data.get('title')
    respondents = data.get('respondents', [])
    emails = [r['email'] for r in respondents]
    if len(emails) != len(set(emails)):
        return jsonify({'code': 'RESPONDENT_DUPLICATE',
                        'message': '受邀者 email 重複'}), 409
    form_id = generate_id()
    invite_code = uuid.uuid4().hex[:6]
    expire_at = data.get('expire_at')
    form = {
        'form_id': form_id,
        'title': title,
        'invite_code': invite_code,
        'created_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'expire_at': expire_at,
        'created_by': request.user_id,
        'respondents': [],
        'responses': []
    }
    for r in respondents:
        person_uid = generate_id()
        form['respondents'].append({
            'person_uid': person_uid,
            'name': r['name'],
            'email': r['email']
        })
    forms[form_id] = form
    invite_map[invite_code] = form_id
    return jsonify({k: form[k] for k in ['form_id', 'title', 'invite_code', 'created_at', 'expire_at']}), 201


@app.route('/forms/<form_id>/invite-code', methods=['POST'])
@auth_required
def regenerate_invite(form_id):
    form = forms.get(form_id)
    if not form:
        return jsonify({'code': 'FORM_NOT_FOUND', 'message': '查無此表單'}), 404
    if form['created_by'] != request.user_id:
        return jsonify({'code': 'FORM_NOT_FOUND', 'message': '查無此表單'}), 404
    invite_code = uuid.uuid4().hex[:6]
    form['invite_code'] = invite_code
    invite_map[invite_code] = form_id
    return jsonify(invite_code)


@app.route('/invite/<code>', methods=['GET'])
def check_invite(code):
    form_id = invite_map.get(code)
    form = forms.get(form_id)
    if not form:
        return jsonify({'code': 'INVITE_EXPIRED', 'message': '邀請碼已過期'}), 410
    result = {k: form[k] for k in ['form_id', 'title', 'invite_code', 'created_at', 'expire_at']}
    result['respondents'] = [
        {'name': r['name'], 'email': r['email']} for r in form['respondents']
    ]
    return jsonify(result)


@app.route('/invite/<code>/responses', methods=['POST'])
def submit_feedback(code):
    form_id = invite_map.get(code)
    form = forms.get(form_id)
    if not form:
        return jsonify({'code': 'FORM_NOT_FOUND', 'message': '查無此表單'}), 404
    data = request.get_json(force=True)
    content = data.get('feedback_content')
    response = {
        'form_id': form_id,
        'person_uid': generate_id(),
        'feedback_content': content
    }
    form['responses'].append(response)
    return '', 201


@app.route('/forms/<form_id>/responses', methods=['GET'])
@auth_required
def list_feedback(form_id):
    form = forms.get(form_id)
    if not form:
        return jsonify({'code': 'FORM_NOT_FOUND', 'message': '查無此表單'}), 404
    if form['created_by'] != request.user_id:
        return jsonify({'code': 'FORM_NOT_FOUND', 'message': '查無此表單'}), 404
    return jsonify(form['responses'])


def create_app():
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
