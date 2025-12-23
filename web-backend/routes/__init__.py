from routes.auth import auth_bp
from routes.detect import detect_bp
from routes.models import models_bp
from routes.datasets import datasets_bp
from routes.users import users_bp
from routes.statistics import statistics_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
    app.register_blueprint(models_bp, url_prefix='/api/models')
    app.register_blueprint(datasets_bp, url_prefix='/api/datasets')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')

