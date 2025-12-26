import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Use instance folder for database (Flask convention)
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(instance_path, "yolo_helmet.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite 连接参数，解决数据库锁定问题
    # 注意：PRAGMA 设置通过 SQLAlchemy 事件监听器在连接创建时自动应用
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 20,  # 增加超时时间到20秒
            'check_same_thread': False,  # 允许多线程访问
        },
        'pool_pre_ping': True,  # 连接前检查连接是否有效
    }
    
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

