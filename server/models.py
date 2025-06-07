"""
資料庫模型定義
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯關係
    forms = db.relationship('Form', backref='creator', lazy=True, cascade='all, delete-orphan')
    tokens = db.relationship('UserToken', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'uniq_id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserToken(db.Model):
    __tablename__ = 'user_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class Form(db.Model):
    __tablename__ = 'forms'
    
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    title = db.Column(db.String(200), nullable=False)
    creator_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    invite_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯關係
    respondents = db.relationship('Respondent', backref='form', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='form', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'creator_id': self.creator_id,
            'invite_code': self.invite_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'respondents': [r.to_dict() for r in self.respondents],
            'feedbacks': [f.to_dict() for f in self.feedbacks]
        }

class Respondent(db.Model):
    __tablename__ = 'respondents'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String(32), db.ForeignKey('forms.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.String(32), db.ForeignKey('forms.id'), nullable=False)
    respondent_name = db.Column(db.String(100), nullable=False)
    respondent_email = db.Column(db.String(120), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'respondent_name': self.respondent_name,
            'respondent_email': self.respondent_email,
            'feedback_text': self.feedback_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
