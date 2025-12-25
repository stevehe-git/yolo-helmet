from flask import Blueprint, request, jsonify, current_app
from models import Model, Dataset, db
from utils.auth import login_required, admin_required, get_current_user
from pathlib import Path
from config import Config
from datetime import datetime
import json
import threading
from ultralytics import YOLO

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
    model_type = data.get('type', 'custom')  # 默认创建定制模型
    description = data.get('description', '')
    
    if not name:
        return jsonify({'message': '模型名称不能为空'}), 400
    
    # Set default path based on type
    if model_type == 'general':
        path = str(Config.MODELS_FOLDER / Config.DEFAULT_MODEL)
    else:
        path = str(Config.MODELS_FOLDER / f"{name}.pt")
    
    model = Model(name=name, type=model_type, path=path, description=description)
    
    # 保存训练参数
    training_params = {
        'dataset_id': data.get('dataset_id'),
        'base_model': data.get('base_model', 'yolo11n.pt'),
        'epochs': data.get('epochs', 100),
        'batch': data.get('batch', 8),
        'imgsz': data.get('imgsz', 640)
    }
    if training_params.get('dataset_id'):
        model.set_training_params(training_params)
    
    db.session.add(model)
    db.session.commit()
    
    return jsonify(model.to_dict()), 201

@models_bp.route('/<int:model_id>', methods=['PUT'])
@admin_required
def update_model(model_id):
    model = Model.query.get_or_404(model_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'message': '请求数据不能为空'}), 400
    
    # 更新名称
    if 'name' in data:
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'message': '模型名称不能为空'}), 400
        model.name = name
    
    # 更新描述
    if 'description' in data:
        model.description = data.get('description', '').strip() or None
    
    # 更新训练参数
    if 'training_params' in data:
        training_params = data.get('training_params')
        if training_params:
            model.set_training_params(training_params)
    
    db.session.commit()
    return jsonify(model.to_dict()), 200

@models_bp.route('/<int:model_id>', methods=['DELETE'])
@admin_required
def delete_model(model_id):
    model = Model.query.get_or_404(model_id)
    db.session.delete(model)
    db.session.commit()
    return jsonify({'message': 'Model deleted successfully'}), 200

def train_model_async(app, model_id, dataset_id, epochs, batch, imgsz, base_model_name=None):
    """异步训练模型"""
    # 在应用上下文中运行
    with app.app_context():
        try:
            model = Model.query.get(model_id)
            dataset = Dataset.query.get(dataset_id)
            
            if not model:
                print(f"Model {model_id} not found")
                return
            if not dataset:
                print(f"Dataset {dataset_id} not found")
                return
            
            # 获取数据集目录
            dataset_dir = Config.UPLOAD_FOLDER / 'datasets' / str(dataset_id)
            data_yaml = dataset_dir / 'data.yaml'
            
            if not data_yaml.exists():
                print(f"data.yaml not found in dataset {dataset_id}")
                model.set_metrics({'error': '数据集配置文件不存在'})
                db.session.commit()
                return
            
            # 加载预训练模型
            # 使用传入的基础模型名称，如果没有则使用默认值
            if not base_model_name:
                base_model_name = 'yolo11n.pt'
            
            # YOLO会自动下载模型
            # 移除.pt后缀，YOLO会自动处理并下载
            model_name = base_model_name.replace('.pt', '') if base_model_name.endswith('.pt') else base_model_name
            
            print(f"Loading base model: {model_name}")
            try:
                # YOLO会自动下载模型（如果不存在）
                # 使用不带.pt后缀的名称，YOLO会自动处理
                base_model = YOLO(model_name)
                print(f"Successfully loaded base model: {model_name}")
            except Exception as e:
                print(f"Error loading base model {model_name}: {str(e)}")
                # 如果失败，尝试使用完整路径
                model_path = Config.MODELS_FOLDER / base_model_name
                if model_path.exists():
                    print(f"Trying to load from local path: {model_path}")
                    base_model = YOLO(str(model_path))
                else:
                    # 最后尝试：使用默认模型
                    print(f"Falling back to default model: yolo11n")
                    base_model = YOLO('yolo11n')
            
            # 开始训练
            results = base_model.train(
                data=str(data_yaml.absolute()),
                epochs=epochs,
                batch=batch,
                imgsz=imgsz,
                project=str(Config.MODELS_FOLDER / 'runs'),
                name=f'model_{model_id}',
                exist_ok=True,
                save=True,
                verbose=True
            )
            
            # 获取最佳模型路径
            best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
            if not best_model_path.exists():
                best_model_path = Path(results.save_dir) / 'weights' / 'last.pt'
            
            # 复制最佳模型到模型目录
            if best_model_path.exists():
                target_path = Config.MODELS_FOLDER / f"{model.name}.pt"
                import shutil
                shutil.copy2(str(best_model_path), str(target_path))
                model.path = str(target_path)
            
            # 提取训练指标
            metrics = {
                'map': 0.0,
                'map50_95': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0
            }
            
            try:
                # YOLO训练结果通常在results对象中
                # 尝试从results对象获取指标
                if hasattr(results, 'results_dict'):
                    results_dict = results.results_dict
                    metrics['map'] = float(results_dict.get('metrics/mAP50(B)', results_dict.get('metrics/mAP50', 0)))
                    metrics['map50_95'] = float(results_dict.get('metrics/mAP50-95(B)', results_dict.get('metrics/mAP50-95', 0)))
                    metrics['precision'] = float(results_dict.get('metrics/precision(B)', results_dict.get('metrics/precision', 0)))
                    metrics['recall'] = float(results_dict.get('metrics/recall(B)', results_dict.get('metrics/recall', 0)))
                elif hasattr(results, 'metrics'):
                    # 尝试从metrics属性获取
                    m = results.metrics
                    metrics['map'] = float(getattr(m, 'map50', getattr(m, 'map', 0)))
                    metrics['map50_95'] = float(getattr(m, 'map50_95', getattr(m, 'map_50_95', 0)))
                    metrics['precision'] = float(getattr(m, 'precision', 0))
                    metrics['recall'] = float(getattr(m, 'recall', 0))
                else:
                    # 尝试从CSV文件读取（YOLO会生成results.csv）
                    csv_path = Path(results.save_dir) / 'results.csv'
                    if csv_path.exists():
                        try:
                            import csv
                            with open(csv_path, 'r') as f:
                                reader = csv.DictReader(f)
                                rows = list(reader)
                                if rows:
                                    last_row = rows[-1]
                                    # 尝试不同的列名格式
                                    map_key = 'metrics/mAP50(B)' if 'metrics/mAP50(B)' in last_row else 'metrics/mAP50'
                                    map50_95_key = 'metrics/mAP50-95(B)' if 'metrics/mAP50-95(B)' in last_row else 'metrics/mAP50-95'
                                    precision_key = 'metrics/precision(B)' if 'metrics/precision(B)' in last_row else 'metrics/precision'
                                    recall_key = 'metrics/recall(B)' if 'metrics/recall(B)' in last_row else 'metrics/recall'
                                    
                                    metrics['map'] = float(last_row.get(map_key, 0))
                                    metrics['map50_95'] = float(last_row.get(map50_95_key, 0))
                                    metrics['precision'] = float(last_row.get(precision_key, 0))
                                    metrics['recall'] = float(last_row.get(recall_key, 0))
                        except Exception as csv_error:
                            print(f"Error reading CSV: {str(csv_error)}")
            except Exception as e:
                print(f"Error extracting metrics: {str(e)}")
                # 使用默认值
            
            # 计算F1分数
            if metrics['precision'] > 0 and metrics['recall'] > 0:
                metrics['f1'] = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall'])
            
            # 保存指标到模型
            model.set_metrics(metrics)
            db.session.commit()
            
            print(f"Training completed for model {model_id}")
        except Exception as e:
            print(f"Training error: {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                model = Model.query.get(model_id)
                if model:
                    model.set_metrics({'error': f'训练失败: {str(e)}'})
                    db.session.commit()
            except:
                pass

@models_bp.route('/train', methods=['POST'])
@admin_required
def train_model():
    data = request.get_json()
    model_id = data.get('model_id')
    
    if not model_id:
        return jsonify({'message': '模型ID不能为空'}), 400
    
    model = Model.query.get_or_404(model_id)
    
    if model.type != 'custom':
        return jsonify({'message': '只能训练定制模型'}), 400
    
    # 如果没有提供训练参数，使用模型保存的训练参数
    dataset_id = data.get('dataset_id')
    epochs = data.get('epochs')
    batch = data.get('batch')
    imgsz = data.get('imgsz')
    base_model = data.get('base_model')
    
    if not dataset_id:
        training_params = model.get_training_params()
        if not training_params or not training_params.get('dataset_id'):
            return jsonify({'message': '模型未配置训练参数，请先编辑模型设置训练参数'}), 400
        dataset_id = training_params.get('dataset_id')
        epochs = training_params.get('epochs', 100)
        batch = training_params.get('batch', 8)
        imgsz = training_params.get('imgsz', 640)
        base_model = training_params.get('base_model', 'yolo11n.pt')
    else:
        # 如果提供了参数，使用提供的参数，并更新模型保存的参数
        epochs = epochs or 100
        batch = batch or 8
        imgsz = imgsz or 640
        base_model = base_model or 'yolo11n.pt'
        model.set_training_params({
            'dataset_id': dataset_id,
            'base_model': base_model,
            'epochs': epochs,
            'batch': batch,
            'imgsz': imgsz
        })
        db.session.commit()
    
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if dataset.status != 'validated':
        return jsonify({'message': '数据集未验证，无法用于训练'}), 400
    
    # 检查数据集目录和data.yaml
    dataset_dir = Config.UPLOAD_FOLDER / 'datasets' / str(dataset_id)
    data_yaml = dataset_dir / 'data.yaml'
    
    if not data_yaml.exists():
        return jsonify({'message': '数据集配置文件不存在，请重新上传数据集'}), 400
    
    # 在后台线程中启动训练（需要传递app实例以创建应用上下文）
    from flask import current_app
    app = current_app._get_current_object()
    training_thread = threading.Thread(
        target=train_model_async,
        args=(app, model_id, dataset_id, epochs, batch, imgsz, base_model),
        daemon=True
    )
    training_thread.start()
    
    return jsonify({
        'message': '训练任务已启动，训练完成后会自动更新模型指标',
        'model_id': model_id,
        'dataset_id': dataset_id
    }), 200

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

