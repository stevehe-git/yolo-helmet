from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Model(db.Model):
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'general' or 'custom'
    path = db.Column(db.String(255), nullable=False)
    metrics_json = db.Column(db.Text)  # JSON string for metrics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_metrics(self):
        if self.metrics_json:
            return json.loads(self.metrics_json)
        return None
    
    def set_metrics(self, metrics):
        self.metrics_json = json.dumps(metrics)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'path': self.path,
            'metrics': self.get_metrics(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_count': self.image_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True)
    detection_type = db.Column(db.String(20), nullable=False)  # 'image', 'video', 'realtime'
    with_helmet = db.Column(db.Integer, default=0)
    without_helmet = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'detection_type': self.detection_type,
            'with_helmet': self.with_helmet,
            'without_helmet': self.without_helmet,
            'total': self.total,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

