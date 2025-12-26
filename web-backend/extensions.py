from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 创建 SQLAlchemy 实例
# 注意：Flask-SQLAlchemy 3.x 在 init_app 时会自动读取配置
# 引擎选项可以通过 SQLALCHEMY_ENGINE_OPTIONS 配置项传递
db = SQLAlchemy()
migrate = Migrate()

