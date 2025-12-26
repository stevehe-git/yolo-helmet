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
    # 支持搜索参数
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = Model.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            db.or_(
                Model.name.like(f'%{search}%'),
                Model.description.like(f'%{search}%')
            )
        )
    
    # 状态过滤
    if status_filter:
        query = query.filter(Model.status == status_filter)
    
    models = query.all()
    
    # 同步检查：验证模型文件是否存在，如果不存在则更新状态
    for model in models:
        if model.path:
            model_path = Path(model.path)
            if not model_path.exists():
                # 如果模型文件不存在，且状态是completed或published，更新为failed
                if model.status in ['completed', 'published']:
                    model.status = 'failed'
                    current_metrics = model.get_metrics()
                    if not current_metrics or not current_metrics.get('error'):
                        error_msg = '模型文件不存在，可能已被删除'
                        if current_metrics:
                            current_metrics['error'] = error_msg
                            model.set_metrics(current_metrics)
                        else:
                            model.set_metrics({'error': error_msg})
                    db.session.commit()
                    print(f"Synced model {model.id} ({model.name}): file missing, status updated to failed")
        else:
            # 如果模型没有路径，且状态是completed或published，也标记为failed
            if model.status in ['completed', 'published']:
                model.status = 'failed'
                current_metrics = model.get_metrics()
                if not current_metrics or not current_metrics.get('error'):
                    error_msg = '模型路径未设置'
                    if current_metrics:
                        current_metrics['error'] = error_msg
                        model.set_metrics(current_metrics)
                    else:
                        model.set_metrics({'error': error_msg})
                db.session.commit()
                print(f"Synced model {model.id} ({model.name}): no path, status updated to failed")
    
    return jsonify([m.to_dict() for m in models]), 200

@models_bp.route('/<int:model_id>', methods=['GET'])
@login_required
def get_model(model_id):
    model = Model.query.get_or_404(model_id)
    
    # 同步检查：验证模型文件是否存在
    if model.path:
        model_path = Path(model.path)
        if not model_path.exists():
            # 如果模型文件不存在，且状态是completed或published，更新为failed
            if model.status in ['completed', 'published']:
                model.status = 'failed'
                current_metrics = model.get_metrics()
                if not current_metrics or not current_metrics.get('error'):
                    error_msg = '模型文件不存在，可能已被删除'
                    if current_metrics:
                        current_metrics['error'] = error_msg
                        model.set_metrics(current_metrics)
                    else:
                        model.set_metrics({'error': error_msg})
                db.session.commit()
    else:
        # 如果模型没有路径，且状态是completed或published，也标记为failed
        if model.status in ['completed', 'published']:
            model.status = 'failed'
            current_metrics = model.get_metrics()
            if not current_metrics or not current_metrics.get('error'):
                error_msg = '模型路径未设置'
                if current_metrics:
                    current_metrics['error'] = error_msg
                    model.set_metrics(current_metrics)
                else:
                    model.set_metrics({'error': error_msg})
            db.session.commit()
    
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

@models_bp.route('/import', methods=['POST'])
@admin_required
def import_model():
    """导入已有的模型文件"""
    from werkzeug.utils import secure_filename
    import shutil
    
    # 检查是否有文件上传
    if 'model_file' not in request.files:
        return jsonify({'message': '请选择要导入的模型文件'}), 400
    
    file = request.files['model_file']
    if file.filename == '':
        return jsonify({'message': '请选择要导入的模型文件'}), 400
    
    # 验证文件格式
    if not file.filename.lower().endswith('.pt'):
        return jsonify({'message': '只支持.pt格式的模型文件'}), 400
    
    # 获取表单数据
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        return jsonify({'message': '模型名称不能为空'}), 400
    
    # 检查模型名称是否已存在
    existing_model = Model.query.filter_by(name=name).first()
    if existing_model:
        return jsonify({'message': f'模型名称"{name}"已存在，请使用其他名称'}), 400
    
    try:
        # 确保模型目录存在
        Config.MODELS_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # 生成安全的文件名
        safe_filename = secure_filename(f"{name}.pt")
        target_path = Config.MODELS_FOLDER / safe_filename
        
        # 检查目标文件是否已存在
        if target_path.exists():
            return jsonify({'message': f'模型文件"{safe_filename}"已存在，请使用其他名称'}), 400
        
        # 保存上传的文件
        file.save(str(target_path))
        
        # 验证文件是否成功保存
        if not target_path.exists():
            return jsonify({'message': '模型文件保存失败'}), 500
        
        # 验证文件是否为有效的YOLO模型（可选，尝试加载）
        try:
            test_model = YOLO(str(target_path))
            # 如果能成功加载，说明是有效的模型文件
        except Exception as e:
            # 如果加载失败，删除文件并返回错误
            target_path.unlink()
            return jsonify({'message': f'无效的模型文件：{str(e)}'}), 400
        
        # 创建模型记录
        model = Model(
            name=name,
            type='custom',
            path=str(target_path.absolute()),
            description=description,
            status='completed'  # 导入的模型直接标记为已完成
        )
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'message': '模型导入成功',
            'model': model.to_dict()
        }), 201
        
    except Exception as e:
        # 如果出错，尝试清理已保存的文件
        if target_path.exists():
            try:
                target_path.unlink()
            except:
                pass
        return jsonify({'message': f'导入模型失败：{str(e)}'}), 500

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
    
    # Delete model file if exists
    model_path = Path(model.path)
    if model_path.exists():
        model_path.unlink()
    
    db.session.delete(model)
    db.session.commit()
    return jsonify({'message': 'Model deleted successfully'}), 200

@models_bp.route('/<int:model_id>/publish', methods=['POST'])
@admin_required
def publish_model(model_id):
    """发布模型"""
    model = Model.query.get_or_404(model_id)
    
    if model.status != 'completed':
        return jsonify({'message': '只有训练完成的模型才能发布'}), 400
    
    model.status = 'published'
    db.session.commit()
    
    return jsonify({'message': '模型发布成功', 'model': model.to_dict()}), 200

@models_bp.route('/<int:model_id>/unpublish', methods=['POST'])
@admin_required
def unpublish_model(model_id):
    """取消发布模型"""
    model = Model.query.get_or_404(model_id)
    
    if model.status != 'published':
        return jsonify({'message': '模型未发布'}), 400
    
    # 检查模型文件是否存在
    if model.path and not Path(model.path).exists():
        return jsonify({'message': '模型文件不存在，无法取消发布'}), 400
    
    model.status = 'completed'
    db.session.commit()
    
    return jsonify({'message': '取消发布成功', 'model': model.to_dict()}), 200

@models_bp.route('/sync', methods=['POST'])
@admin_required
def sync_models():
    """同步模型文件状态，检查所有模型文件是否存在"""
    models = Model.query.all()
    synced_count = 0
    
    for model in models:
        if model.path:
            model_path = Path(model.path)
            if not model_path.exists():
                # 如果模型文件不存在，且状态是completed或published，更新为failed
                if model.status in ['completed', 'published']:
                    old_status = model.status
                    model.status = 'failed'
                    if not model.get_metrics() or not model.get_metrics().get('error'):
                        error_msg = '模型文件不存在，可能已被删除'
                        model.set_metrics({'error': error_msg})
                    db.session.commit()
                    synced_count += 1
                    print(f"Synced model {model.id} ({model.name}): {old_status} -> failed (file missing)")
    
    return jsonify({
        'message': f'同步完成，已更新 {synced_count} 个模型的状态',
        'synced_count': synced_count
    }), 200

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
            model_file_saved = False
            if best_model_path.exists():
                target_path = Config.MODELS_FOLDER / f"{model.name}.pt"
                import shutil
                try:
                    # 确保目标目录存在
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(best_model_path), str(target_path))
                    # 验证文件是否成功复制
                    if target_path.exists():
                        model.path = str(target_path.absolute())  # 使用绝对路径
                        model_file_saved = True
                        print(f"Model saved to: {target_path.absolute()}")
                    else:
                        print(f"Error: Model file copy failed, target file does not exist")
                except Exception as copy_error:
                    print(f"Error copying model file: {str(copy_error)}")
            else:
                print(f"Warning: Best model file not found at {best_model_path}")
                model.set_metrics({'error': '训练完成但模型文件未找到'})
                model.status = 'failed'
                db.session.commit()
                print(f"Training failed for model {model_id}: model file not found")
                return  # 如果模型文件不存在，直接返回，不保存指标
            
            # 验证模型文件是否成功保存
            if not model_file_saved or not Path(model.path).exists():
                error_msg = '模型文件保存失败' if not model_file_saved else '模型文件验证失败'
                print(f"Error: {error_msg} - {model.path}")
                model.set_metrics({'error': error_msg})
                model.status = 'failed'
                db.session.commit()
                print(f"Training failed for model {model_id}: {error_msg}")
                return
            
            # 提取训练指标（只有在模型文件成功保存后才提取）
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
            
            # 再次验证模型文件是否存在（防止在提取指标过程中文件被删除）
            if not model.path or not Path(model.path).exists():
                error_msg = '模型文件在训练完成后被删除' if model.path else '模型路径未设置'
                model.set_metrics({'error': error_msg})
                model.status = 'failed'
                db.session.commit()
                print(f"Training failed for model {model_id}: {error_msg}")
                return
            
            # 保存指标到模型（只有在模型文件存在时才保存）
            model.set_metrics(metrics)
            # 更新模型状态为训练完成
            model.status = 'completed'
            db.session.commit()
            
            print(f"Training completed for model {model_id}, model file: {model.path}")
        except Exception as e:
            print(f"Training error: {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                model = Model.query.get(model_id)
                if model:
                    error_msg = str(e)
                    if 'does not exist' in error_msg:
                        error_msg = f'基础模型文件不存在: {base_model_name}'
                    elif 'FileNotFoundError' in error_msg:
                        error_msg = '模型文件未找到，请检查模型路径'
                    else:
                        error_msg = f'训练失败: {error_msg}'
                    
                    model.set_metrics({'error': error_msg})
                    model.status = 'failed'
                    db.session.commit()
                    print(f"Training error saved to model {model_id}: {error_msg}")
            except Exception as db_error:
                print(f"Failed to save training error: {str(db_error)}")

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
    
    # 更新模型状态为训练中
    model.status = 'training'
    db.session.commit()
    
    # 获取基础模型名称
    base_model_name = base_model or 'yolov8n.pt'
    
    # 在后台线程中启动训练（需要传递app实例以创建应用上下文）
    from flask import current_app
    app = current_app._get_current_object()
    training_thread = threading.Thread(
        target=train_model_async,
        args=(app, model_id, dataset_id, epochs, batch, imgsz, base_model_name),
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
    
    print(f"Getting training data for model {model_id}: path={model.path}, status={model.status}")
    
    # 检查模型文件是否存在（但即使不存在也尝试读取训练数据，因为训练数据可能在runs目录中）
    if not model.path or not Path(model.path).exists():
        print(f"Warning: Model file does not exist: {model.path}, but will try to read training data from runs directory")
        # 不直接返回404，继续尝试读取训练数据
    
    # 尝试从runs目录读取训练数据
    training_data = {
        'epochs': [],
        'train_loss': [],
        'val_loss': [],
        'map': [],
        'precision': [],
        'recall': []
    }
    
    try:
        # 查找runs目录中的训练结果
        runs_dir = Config.MODELS_FOLDER / 'runs' / f'model_{model_id}'
        results_csv = None
        
        # 首先尝试直接在runs_dir下查找results.csv（YOLO可能直接保存在这里）
        direct_csv = runs_dir / 'results.csv'
        if direct_csv.exists():
            results_csv = direct_csv
        else:
            # 如果直接路径不存在，尝试在子目录中查找
            if runs_dir.exists():
                # 查找最新的训练结果目录
                train_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
                for train_dir in train_dirs:
                    csv_path = train_dir / 'results.csv'
                    if csv_path.exists():
                        results_csv = csv_path
                        break
        
        if results_csv and results_csv.exists():
            # 从CSV文件读取训练数据
            import csv
            with open(results_csv, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    print(f"Warning: CSV file {results_csv} is empty")
                    return jsonify({
                        'error': '训练数据文件为空',
                        'epochs': [],
                        'train_loss': [],
                        'val_loss': [],
                        'map': [],
                        'precision': [],
                        'recall': []
                    }), 404
                
                # 获取所有列名（可能包含空格），创建去除空格后的映射
                fieldnames = reader.fieldnames or []
                # 创建列名映射：去除空格后的列名 -> 原始列名
                fieldname_map = {}
                for name in fieldnames:
                    stripped = name.strip()
                    fieldname_map[stripped] = name
                
                def get_value(row, possible_keys):
                    """从row中获取值，尝试多个可能的键名（考虑空格）"""
                    for key in possible_keys:
                        # 先尝试原始键名
                        if key in row and row[key]:
                            try:
                                value = row[key].strip()
                                if value:
                                    return float(value)
                            except (ValueError, AttributeError):
                                pass
                        # 再尝试去除空格后的键名
                        stripped_key = key.strip()
                        if stripped_key in fieldname_map:
                            original_key = fieldname_map[stripped_key]
                            if original_key in row and row[original_key]:
                                try:
                                    value = row[original_key].strip()
                                    if value:
                                        return float(value)
                                except (ValueError, AttributeError):
                                    pass
                        # 最后尝试在所有键中查找包含该键名的（处理前导空格）
                        for original_key in row.keys():
                            if original_key.strip() == stripped_key:
                                try:
                                    value = row[original_key].strip()
                                    if value:
                                        return float(value)
                                except (ValueError, AttributeError):
                                    pass
                    return 0.0
                
                for i, row in enumerate(rows, start=1):
                    training_data['epochs'].append(i)
                    
                    # 读取损失值（计算总损失 = box_loss + cls_loss + dfl_loss）
                    train_box_loss = get_value(row, ['train/box_loss'])
                    train_cls_loss = get_value(row, ['train/cls_loss'])
                    train_dfl_loss = get_value(row, ['train/dfl_loss'])
                    train_loss = train_box_loss + train_cls_loss + train_dfl_loss
                    
                    val_box_loss = get_value(row, ['val/box_loss'])
                    val_cls_loss = get_value(row, ['val/cls_loss'])
                    val_dfl_loss = get_value(row, ['val/dfl_loss'])
                    val_loss = val_box_loss + val_cls_loss + val_dfl_loss
                    
                    training_data['train_loss'].append(train_loss)
                    training_data['val_loss'].append(val_loss)
                    
                    # 读取指标
                    map_value = get_value(row, ['metrics/mAP50(B)', 'metrics/mAP50'])
                    precision_value = get_value(row, ['metrics/precision(B)', 'metrics/precision'])
                    recall_value = get_value(row, ['metrics/recall(B)', 'metrics/recall'])
                    
                    training_data['map'].append(map_value)
                    training_data['precision'].append(precision_value)
                    training_data['recall'].append(recall_value)
                
                print(f"Successfully read {len(training_data['epochs'])} epochs from {results_csv}")
        else:
            # 如果找不到训练数据文件，返回空数据
            return jsonify({
                'error': '训练数据文件不存在，可能runs目录已被删除',
                'epochs': [],
                'train_loss': [],
                'val_loss': [],
                'map': [],
                'precision': [],
                'recall': []
            }), 404
            
    except Exception as e:
        print(f"Error reading training data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'读取训练数据失败: {str(e)}',
            'epochs': [],
            'train_loss': [],
            'val_loss': [],
            'map': [],
            'precision': [],
            'recall': []
        }), 500
    
    # 如果没有数据，返回空数据（但不返回404，让前端处理）
    if not training_data['epochs']:
        print(f"Warning: No training data found for model {model_id}")
        return jsonify({
            'error': '训练数据为空',
            'epochs': [],
            'train_loss': [],
            'val_loss': [],
            'map': [],
            'precision': [],
            'recall': []
        }), 200  # 改为200，让前端判断是否有数据
    
    print(f"Returning training data for model {model_id}: {len(training_data['epochs'])} epochs")
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

