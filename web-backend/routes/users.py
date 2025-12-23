from flask import Blueprint, request, jsonify
from models import User, db
from utils.auth import login_required, admin_required
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@admin_required
def get_users():
    try:
        users = User.query.all()
        return jsonify([u.to_dict() for u in users]), 200
    except Exception as e:
        return jsonify({'message': f'获取用户列表失败：{str(e)}'}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'message': f'获取用户信息失败：{str(e)}'}), 500

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        if email and User.query.filter_by(email=email).first():
            return jsonify({'message': '邮箱已被使用'}), 400
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        error_msg = str(e.orig)
        if 'email' in error_msg.lower() or 'UNIQUE constraint failed: users.email' in error_msg:
            return jsonify({'message': '邮箱已被使用，请使用其他邮箱'}), 400
        elif 'username' in error_msg.lower() or 'UNIQUE constraint failed: users.username' in error_msg:
            return jsonify({'message': '用户名已存在'}), 400
        else:
            return jsonify({'message': '创建用户失败：数据冲突'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建用户失败：{str(e)}'}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'email' in data:
            email = data['email']
            # 检查邮箱是否被其他用户使用
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'message': '邮箱已被其他用户使用'}), 400
            user.email = email
        if 'role' in data:
            user.role = data['role']
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except IntegrityError as e:
        db.session.rollback()
        error_msg = str(e.orig)
        if 'email' in error_msg.lower() or 'UNIQUE constraint failed: users.email' in error_msg:
            return jsonify({'message': '邮箱已被使用，请使用其他邮箱'}), 400
        else:
            return jsonify({'message': '更新用户失败：数据冲突'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新用户失败：{str(e)}'}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '删除用户成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除用户失败：{str(e)}'}), 500

