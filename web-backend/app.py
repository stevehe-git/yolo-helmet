from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, migrate
from routes import register_routes
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置 SQLite 连接参数，解决数据库锁定问题
    # 使用事件监听器在每次创建连接时设置 PRAGMA
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """为每个 SQLite 连接设置 PRAGMA，解决数据库锁定问题"""
        if isinstance(dbapi_conn, sqlite3.Connection):
            cursor = dbapi_conn.cursor()
            try:
                # 启用 WAL 模式（Write-Ahead Logging）以提高并发性能
                # WAL 模式允许多个读取器和一个写入器同时访问数据库
                cursor.execute("PRAGMA journal_mode=WAL")
                # 设置忙等待超时时间为 20 秒（20000 毫秒）
                # 当数据库被锁定时，等待最多 20 秒而不是立即失败
                cursor.execute("PRAGMA busy_timeout=20000")
                # 设置同步模式为 NORMAL（平衡性能和安全性）
                # NORMAL 模式在 WAL 模式下是安全的，性能更好
                cursor.execute("PRAGMA synchronous=NORMAL")
                # 设置外键约束检查
                cursor.execute("PRAGMA foreign_keys=ON")
            except Exception as e:
                # 如果设置 PRAGMA 失败，记录警告但不阻止连接
                print(f"Warning: Could not set SQLite PRAGMA: {e}")
            finally:
                cursor.close()
    
    # Initialize extensions
    db.init_app(app)
    
    # 配置 SQLite 引擎的连接参数，解决数据库锁定问题
    # Flask-SQLAlchemy 3.x 可能不支持 SQLALCHEMY_ENGINE_OPTIONS 配置项
    # 需要在 init_app 之后手动配置引擎
    with app.app_context():
        if hasattr(Config, 'SQLALCHEMY_ENGINE_OPTIONS'):
            try:
                from sqlalchemy import create_engine
                db_uri = app.config['SQLALCHEMY_DATABASE_URI']
                engine_options = Config.SQLALCHEMY_ENGINE_OPTIONS
                # 创建新引擎并替换 Flask-SQLAlchemy 的引擎
                new_engine = create_engine(db_uri, **engine_options)
                db.engine = new_engine
            except Exception as e:
                print(f"Warning: Could not configure SQLite engine options: {e}")
                # 即使配置失败，事件监听器中的 PRAGMA 设置仍然有效
    
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register routes
    register_routes(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Use 'stat' reloader instead of 'watchdog' to avoid monitoring uploads directory
    # This prevents ERR_UPLOAD_FILE_CHANGED errors during file uploads
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True, reloader_type='stat')

