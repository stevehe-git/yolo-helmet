from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import Dataset, db
from utils.auth import login_required, admin_required
from pathlib import Path
from config import Config
from datetime import datetime
import os
import zipfile
import shutil
import tempfile

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

@datasets_bp.route('/<int:dataset_id>', methods=['PUT'])
@admin_required
def update_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'message': '请求数据不能为空'}), 400
    
    # 更新名称
    if 'name' in data:
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'message': '数据集名称不能为空'}), 400
        # 检查名称是否已被其他数据集使用
        existing = Dataset.query.filter(Dataset.name == name, Dataset.id != dataset_id).first()
        if existing:
            return jsonify({'message': '数据集名称已存在'}), 400
        dataset.name = name
    
    # 更新描述
    if 'description' in data:
        dataset.description = data.get('description', '').strip() or None
    
    db.session.commit()
    return jsonify(dataset.to_dict()), 200

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

def count_images_in_directory(directory):
    """统计目录中的图片数量"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                count += 1
    return count

def validate_dataset_structure(dataset_dir):
    """验证数据集目录结构是否符合要求"""
    errors = []
    warnings = []
    
    # 检查data.yaml（可选，但推荐）
    data_yaml = dataset_dir / 'data.yaml'
    if not data_yaml.exists():
        warnings.append('未找到data.yaml配置文件（可选）')
    
    # 检查必需的目录结构
    required_dirs = {
        'train/images': '训练图片目录',
        'train/labels': '训练标签目录',
        'valid/images': '验证图片目录',
        'valid/labels': '验证标签目录'
    }
    
    optional_dirs = {
        'test/images': '测试图片目录',
        'test/labels': '测试标签目录'
    }
    
    for dir_path, desc in required_dirs.items():
        full_path = dataset_dir / dir_path
        if not full_path.exists() or not full_path.is_dir():
            errors.append(f'缺少必需目录: {dir_path} ({desc})')
    
    for dir_path, desc in optional_dirs.items():
        full_path = dataset_dir / dir_path
        if not full_path.exists() or not full_path.is_dir():
            warnings.append(f'缺少可选目录: {dir_path} ({desc})')
    
    return errors, warnings

def analyze_dataset_structure(dataset_dir):
    """分析数据集目录结构，返回训练/验证/测试集统计"""
    train_count = 0
    val_count = 0
    test_count = 0
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    
    # 优先检查标准结构: train/images, valid/images, test/images
    train_images_dir = dataset_dir / 'train' / 'images'
    valid_images_dir = dataset_dir / 'valid' / 'images'
    test_images_dir = dataset_dir / 'test' / 'images'
    
    if train_images_dir.exists() and train_images_dir.is_dir():
        train_count = count_images_in_directory(train_images_dir)
    
    if valid_images_dir.exists() and valid_images_dir.is_dir():
        val_count = count_images_in_directory(valid_images_dir)
    
    if test_images_dir.exists() and test_images_dir.is_dir():
        test_count = count_images_in_directory(test_images_dir)
    
    # 如果没有找到标准结构，尝试其他常见结构
    if train_count == 0 and val_count == 0 and test_count == 0:
        # 检查是否有train/val/test目录（直接包含图片）
        for item in dataset_dir.iterdir():
            if not item.is_dir():
                continue
            
            dir_name = item.name.lower()
            count = 0
            
            # 如果是train/valid/test目录，统计其中的图片
            if dir_name in ['train', 'training']:
                count = count_images_in_directory(item)
                train_count += count
            elif dir_name in ['val', 'validation', 'valid']:
                count = count_images_in_directory(item)
                val_count += count
            elif dir_name in ['test', 'testing']:
                count = count_images_in_directory(item)
                test_count += count
    
    # 如果仍然没有找到，统计根目录下的所有图片并分配
    if train_count == 0 and val_count == 0 and test_count == 0:
        total = count_images_in_directory(dataset_dir)
        if total > 0:
            # 默认分配：70%训练，20%验证，10%测试
            train_count = int(total * 0.7)
            val_count = int(total * 0.2)
            test_count = total - train_count - val_count
    
    return train_count, val_count, test_count

@datasets_bp.route('/<int:dataset_id>/upload', methods=['POST'])
@admin_required
def upload_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if 'file' not in request.files and 'zip' not in request.files:
        return jsonify({'message': '未提供文件'}), 400
    
    # 优先检查ZIP文件
    zip_file = request.files.get('zip') or request.files.get('file')
    if not zip_file or zip_file.filename == '':
        return jsonify({'message': '未选择文件'}), 400
    
    # 检查文件扩展名
    filename = secure_filename(zip_file.filename)
    if not filename.lower().endswith('.zip'):
        return jsonify({'message': '只支持ZIP格式文件'}), 400
    
    dataset_dir = Config.UPLOAD_FOLDER / 'datasets' / str(dataset_id)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # 使用临时目录保存ZIP文件，避免触发Flask reloader
    temp_dir = Path(tempfile.gettempdir())
    temp_zip_path = temp_dir / f'dataset_{dataset_id}_{filename}'
    
    try:
        # 先保存到临时目录
        zip_file.save(str(temp_zip_path))
        
        # 计算ZIP文件大小
        file_size = os.path.getsize(temp_zip_path)
        
        # 移动到最终位置（原子操作，减少触发reloader的机会）
        zip_path = dataset_dir / filename
        if zip_path.exists():
            zip_path.unlink()
        shutil.move(str(temp_zip_path), str(zip_path))
        
        # 解压ZIP文件
        extract_dir = dataset_dir / 'extracted'
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # 如果解压后的目录只有一个子目录，移动到dataset_dir根目录
        extracted_items = list(extract_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            # 将子目录内容移动到dataset_dir
            for item in extracted_items[0].iterdir():
                dest = dataset_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.move(str(item), str(dest))
                else:
                    shutil.move(str(item), str(dest))
            shutil.rmtree(extract_dir)
        else:
            # 将extracted目录内容移动到dataset_dir
            for item in extract_dir.iterdir():
                dest = dataset_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
            shutil.rmtree(extract_dir)
        
        # 验证数据集结构
        errors, warnings = validate_dataset_structure(dataset_dir)
        if errors:
            # 如果有必需目录缺失，返回错误
            return jsonify({
                'message': '数据集格式不符合要求',
                'errors': errors,
                'warnings': warnings
            }), 400
        
        # 分析数据集结构
        train_count, val_count, test_count = analyze_dataset_structure(dataset_dir)
        total_count = train_count + val_count + test_count
        
        # 更新数据集信息
        dataset.image_count = total_count
        dataset.file_size = file_size
        dataset.train_count = train_count
        dataset.val_count = val_count
        dataset.test_count = test_count
        dataset.status = 'validated' if total_count > 0 else 'failed'
        
        db.session.commit()
        
        # 删除ZIP文件（可选，保留原始ZIP文件）
        # zip_path.unlink()
        
        response_message = f'数据集上传成功，共 {total_count} 张图片'
        if warnings:
            response_message += f'（警告: {"; ".join(warnings)}）'
        
        return jsonify({
            'message': response_message,
            'image_count': total_count,
            'train_count': train_count,
            'val_count': val_count,
            'test_count': test_count,
            'file_size': file_size,
            'status': dataset.status,
            'warnings': warnings if warnings else []
        }), 200
        
    except zipfile.BadZipFile:
        # 清理临时文件
        if temp_zip_path.exists():
            temp_zip_path.unlink()
        return jsonify({'message': 'ZIP文件格式错误或已损坏'}), 400
    except Exception as e:
        db.session.rollback()
        # 清理临时文件
        if temp_zip_path.exists():
            temp_zip_path.unlink()
        return jsonify({'message': f'处理ZIP文件失败: {str(e)}'}), 500

