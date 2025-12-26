from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
from config import Config
from utils.auth import login_required, get_current_user
from utils.detection import DetectionService
from models import Detection, Model, db
from datetime import datetime
import os

detect_bp = Blueprint('detect', __name__)

# Global detection service instance
detection_service = None
realtime_active = False

def get_detection_service(model_id=None):
    global detection_service
    if model_id:
        model = Model.query.get(model_id)
        if not model:
            raise ValueError(f'模型 ID {model_id} 不存在')
        if not Path(model.path).exists():
            raise FileNotFoundError(f'模型文件不存在: {model.path}')
        try:
            return DetectionService(model.path)
        except Exception as e:
            raise RuntimeError(f'无法加载模型: {str(e)}')
    return DetectionService()

@detect_bp.route('/image', methods=['POST'])
@login_required
def detect_image():
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    model_id = request.form.get('model_id', type=int)
    if model_id is None:
        return jsonify({'message': '请选择模型'}), 400
    
    confidence = request.form.get('confidence', type=float)
    if confidence is None:
        confidence = Config.CONFIDENCE_THRESHOLD
    user = get_current_user()
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = Config.UPLOAD_FOLDER / 'images' / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    file.save(filepath)
    
    try:
        # Perform detection
        service = get_detection_service(model_id)
        result = service.detect_image(str(filepath), confidence=confidence)
        
        # Save detection record
        detection = Detection(
            user_id=user.id if user else None,
            model_id=model_id,
            detection_type='image',
            with_helmet=result['stats']['with_helmet'],
            without_helmet=result['stats']['without_helmet'],
            total=result['stats']['total']
        )
        db.session.add(detection)
        db.session.commit()
        
        return jsonify(result), 200
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        # 模型相关错误
        import traceback
        print(f"Model error in detect_image: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'模型错误: {str(e)}'}), 400
    except Exception as e:
        # 其他错误，记录详细日志
        import traceback
        print(f"Detection error in detect_image: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'检测失败: {str(e)}'}), 500
    finally:
        # Clean up uploaded file
        if filepath.exists():
            filepath.unlink()

@detect_bp.route('/video', methods=['POST'])
@login_required
def detect_video():
    if 'video' not in request.files:
        return jsonify({'message': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    model_id = request.form.get('model_id', type=int)
    if model_id is None:
        return jsonify({'message': '请选择模型'}), 400
    
    confidence = request.form.get('confidence', type=float)
    if confidence is None:
        confidence = Config.CONFIDENCE_THRESHOLD
    
    detection_fps = request.form.get('detection_fps', type=int)
    if detection_fps is None:
        detection_fps = 10  # 默认10 FPS
    
    user = get_current_user()
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = Config.UPLOAD_FOLDER / 'videos' / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    file.save(filepath)
    
    try:
        # Perform detection
        service = get_detection_service(model_id)
        # 设置置信度阈值
        service.confidence_threshold = float(confidence)
        output_path = Config.UPLOAD_FOLDER / 'results' / f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        result = service.detect_video(str(filepath), str(output_path), detection_fps=detection_fps)
        
        # Save detection record
        detection = Detection(
            user_id=user.id if user else None,
            model_id=model_id,
            detection_type='video',
            with_helmet=result['summary']['with_helmet'],
            without_helmet=result['summary']['without_helmet'],
            total=result['summary']['total_detections']
        )
        db.session.add(detection)
        db.session.commit()
        
        return jsonify(result), 200
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        # 模型相关错误
        return jsonify({'message': f'模型错误: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'message': f'检测失败: {str(e)}'}), 500
    finally:
        # Clean up uploaded file
        if filepath.exists():
            filepath.unlink()

@detect_bp.route('/realtime/start', methods=['POST'])
@login_required
def start_realtime():
    global realtime_active, detection_service
    data = request.get_json()
    model_id = data.get('model_id') if data else None
    confidence = data.get('confidence', 0.25) if data else 0.25  # 默认0.25
    fps = data.get('fps', 5) if data else 5  # 默认5 FPS
    
    try:
        # 验证模型并初始化检测服务
        if model_id:
            detection_service = get_detection_service(model_id)
        else:
            detection_service = get_detection_service()
        
        # 设置置信度阈值和FPS
        if detection_service:
            detection_service.confidence_threshold = float(confidence)
            detection_service.detection_fps = int(fps)
        
        realtime_active = True
        return jsonify({'message': 'Realtime detection started'}), 200
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        return jsonify({'message': f'模型错误: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'message': f'启动失败: {str(e)}'}), 500

@detect_bp.route('/realtime/stop', methods=['POST'])
@login_required
def stop_realtime():
    global realtime_active
    realtime_active = False
    return jsonify({'message': 'Realtime detection stopped'}), 200

@detect_bp.route('/realtime/frame', methods=['POST'])
@login_required
def get_realtime_frame():
    global realtime_active, detection_service
    if not realtime_active:
        return jsonify({'message': 'Realtime detection not active'}), 400
    
    if not detection_service:
        return jsonify({'message': 'Detection service not initialized'}), 400
    
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # 获取置信度和FPS参数
    confidence = request.form.get('confidence', type=float)
    fps = request.form.get('fps', type=int)
    if confidence is not None:
        detection_service.confidence_threshold = float(confidence)
    if fps is not None:
        detection_service.detection_fps = int(fps)
    
    try:
        # 保存临时文件
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # 执行检测
            result = detection_service.detect_image(tmp_path, confidence=detection_service.confidence_threshold)
            
            return jsonify({
                'image': result['image'],
                'detections': result['detections']
            }), 200
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except Exception as e:
        import traceback
        print(f"Error in realtime frame detection: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'检测失败: {str(e)}'}), 500

@detect_bp.route('/uploads/results/<filename>', methods=['GET', 'OPTIONS'])
def get_result_file(filename):
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # 安全地处理文件名，防止路径遍历攻击
    # 注意：secure_filename可能会改变文件名，所以先保存原始文件名用于日志
    original_filename = filename
    safe_filename = secure_filename(filename)
    filepath = Config.UPLOAD_FOLDER / 'results' / safe_filename
    
    # 如果secure_filename改变了文件名，尝试使用原始文件名
    if not filepath.exists() and safe_filename != original_filename:
        filepath = Config.UPLOAD_FOLDER / 'results' / original_filename
    
    if not filepath.exists():
        print(f"Video file not found: {filepath.absolute()}")
        print(f"Looking for: {original_filename}")
        print(f"Safe filename: {safe_filename}")
        # 列出目录中的文件以便调试
        results_dir = Config.UPLOAD_FOLDER / 'results'
        if results_dir.exists():
            files = list(results_dir.glob('*.mp4'))
            print(f"Available files: {[f.name for f in files[:5]]}")
        return jsonify({'message': f'File not found: {original_filename}'}), 404
    
    try:
        # 设置正确的响应头，支持视频流式传输
        response = send_file(
            str(filepath.absolute()), 
            mimetype='video/mp4',
            as_attachment=False,
            conditional=True  # 支持条件请求（If-Modified-Since等）
        )
        # 添加CORS头
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        # 支持Range请求（视频流式播放必需）
        response.headers['Accept-Ranges'] = 'bytes'
        # 设置缓存控制
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    except Exception as e:
        print(f"Error serving video file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error serving file: {str(e)}'}), 500

