from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import Dataset, db
from utils.auth import login_required, admin_required
from pathlib import Path
from config import Config
from datetime import datetime
import os

datasets_bp = Blueprint('datasets', __name__)

@datasets_bp.route('', methods=['GET'])
@login_required
def get_datasets():
    datasets = Dataset.query.all()
    return jsonify([d.to_dict() for d in datasets]), 200

@datasets_bp.route('/<int:dataset_id>', methods=['GET'])
@login_required
def get_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    return jsonify(dataset.to_dict()), 200

@datasets_bp.route('', methods=['POST'])
@admin_required
def create_dataset():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    
    if not name:
        return jsonify({'message': 'Dataset name is required'}), 400
    
    dataset = Dataset(name=name, description=description)
    db.session.add(dataset)
    db.session.commit()
    
    # Create dataset directory
    dataset_dir = Config.UPLOAD_FOLDER / 'datasets' / str(dataset.id)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    return jsonify(dataset.to_dict()), 201

@datasets_bp.route('/<int:dataset_id>', methods=['DELETE'])
@admin_required
def delete_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    # Delete dataset directory
    dataset_dir = Config.UPLOAD_FOLDER / 'datasets' / str(dataset_id)
    if dataset_dir.exists():
        import shutil
        shutil.rmtree(dataset_dir)
    
    db.session.delete(dataset)
    db.session.commit()
    return jsonify({'message': 'Dataset deleted successfully'}), 200

@datasets_bp.route('/<int:dataset_id>/upload', methods=['POST'])
@admin_required
def upload_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if 'images' not in request.files:
        return jsonify({'message': 'No images provided'}), 400
    
    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        return jsonify({'message': 'No files selected'}), 400
    
    dataset_dir = Config.UPLOAD_FOLDER / 'datasets' / str(dataset_id)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = dataset_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(filepath)
            count += 1
    
    dataset.image_count += count
    db.session.commit()
    
    return jsonify({
        'message': f'{count} images uploaded successfully',
        'image_count': dataset.image_count
    }), 200

