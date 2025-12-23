import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///yolo_helmet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = Path('uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    
    # Model settings
    MODELS_FOLDER = Path('models')
    DEFAULT_MODEL = 'yolo11n.pt'
    
    # Detection settings
    CONFIDENCE_THRESHOLD = 0.25
    IOU_THRESHOLD = 0.45
    
    # Create necessary directories
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    MODELS_FOLDER.mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'images').mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'videos').mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'results').mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'datasets').mkdir(exist_ok=True)

