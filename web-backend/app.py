from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, migrate
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
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

