from flask import Blueprint, request, jsonify
from models import User, db
from utils.auth import login_required, admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

