from flask import Blueprint, request, jsonify
from models import Model, db
from utils.auth import login_required, admin_required, get_current_user
from pathlib import Path
from config import Config
from datetime import datetime
import json

models_bp = Blueprint('models', __name__)

@models_bp.route('', methods=['GET'])
@login_required
def get_models():
    models = Model.query.all()
    return jsonify([m.to_dict() for m in models]), 200

@models_bp.route('/<int:model_id>', methods=['GET'])
@login_required
def get_model(model_id):
    model = Model.query.get_or_404(model_id)
    return jsonify(model.to_dict()), 200

@models_bp.route('', methods=['POST'])
@admin_required
def create_model():
    data = request.get_json()
    name = data.get('name')
    model_type = data.get('type', 'general')
    
    if not name:
        return jsonify({'message': 'Model name is required'}), 400
    
    # Set default path based on type
    if model_type == 'general':
        path = str(Config.MODELS_FOLDER / Config.DEFAULT_MODEL)
    else:
        path = str(Config.MODELS_FOLDER / f"{name}.pt")
    
    model = Model(name=name, type=model_type, path=path)
    db.session.add(model)
    db.session.commit()
    
    return jsonify(model.to_dict()), 201

@models_bp.route('/<int:model_id>', methods=['DELETE'])
@admin_required
def delete_model(model_id):
    model = Model.query.get_or_404(model_id)
    db.session.delete(model)
    db.session.commit()
    return jsonify({'message': 'Model deleted successfully'}), 200

@models_bp.route('/train', methods=['POST'])
@admin_required
def train_model():
    data = request.get_json()
    model_id = data.get('model_id')
    dataset_id = data.get('dataset_id')
    epochs = data.get('epochs', 100)
    
    # This is a placeholder - actual training would be implemented here
    return jsonify({'message': 'Training started'}), 200

@models_bp.route('/<int:model_id>/training', methods=['GET'])
@login_required
def get_model_training_data(model_id):
    model = Model.query.get_or_404(model_id)
    
    # Return mock training data
    training_data = {
        'epochs': list(range(1, 101)),
        'train_loss': [0.5 - i * 0.004 for i in range(100)],
        'val_loss': [0.6 - i * 0.003 for i in range(100)],
        'map': [0.3 + i * 0.006 for i in range(100)],
        'precision': [0.4 + i * 0.005 for i in range(100)],
        'recall': [0.35 + i * 0.0055 for i in range(100)]
    }
    
    return jsonify(training_data), 200

@models_bp.route('/<int:model_id>/metrics', methods=['GET'])
@login_required
def get_model_metrics(model_id):
    model = Model.query.get_or_404(model_id)
    
    # Return mock metrics if not set
    if not model.get_metrics():
        metrics = {
            'map': 0.85,
            'precision': 0.88,
            'recall': 0.82,
            'f1': 0.85
        }
        model.set_metrics(metrics)
        db.session.commit()
    
    return jsonify(model.get_metrics()), 200

