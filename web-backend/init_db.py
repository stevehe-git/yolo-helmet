"""
Initialize database and create default admin user
"""
from app import create_app
from models import User, db

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: username=admin, password=admin123')
    else:
        print('Admin user already exists')
    
    # Create default general model
    from models import Model
    general_model = Model.query.filter_by(name='通用安全帽检测模型').first()
    if not general_model:
        general_model = Model(
            name='通用安全帽检测模型',
            type='general',
            path='yolo11n.pt'
        )
        db.session.add(general_model)
        db.session.commit()
        print('Default model created')
    else:
        print('Default model already exists')
    
    print('Database initialized successfully!')

