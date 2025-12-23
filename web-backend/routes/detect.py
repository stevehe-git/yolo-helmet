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
        if model and Path(model.path).exists():
            return DetectionService(model.path)
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
    user = get_current_user()
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = Config.UPLOAD_FOLDER / 'images' / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    file.save(filepath)
    
    try:
        # Perform detection
        service = get_detection_service(model_id)
        result = service.detect_image(str(filepath))
        
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
    except Exception as e:
        return jsonify({'message': f'Detection failed: {str(e)}'}), 500
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
    user = get_current_user()
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = Config.UPLOAD_FOLDER / 'videos' / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    file.save(filepath)
    
    try:
        # Perform detection
        service = get_detection_service(model_id)
        output_path = Config.UPLOAD_FOLDER / 'results' / f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        result = service.detect_video(str(filepath), str(output_path))
        
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
    except Exception as e:
        return jsonify({'message': f'Detection failed: {str(e)}'}), 500
    finally:
        # Clean up uploaded file
        if filepath.exists():
            filepath.unlink()

@detect_bp.route('/realtime/start', methods=['POST'])
@login_required
def start_realtime():
    global realtime_active
    data = request.get_json()
    model_id = data.get('model_id') if data else None
    
    realtime_active = True
    return jsonify({'message': 'Realtime detection started'}), 200

@detect_bp.route('/realtime/stop', methods=['POST'])
@login_required
def stop_realtime():
    global realtime_active
    realtime_active = False
    return jsonify({'message': 'Realtime detection stopped'}), 200

@detect_bp.route('/realtime/frame', methods=['GET'])
@login_required
def get_realtime_frame():
    global realtime_active
    if not realtime_active:
        return jsonify({'message': 'Realtime detection not active'}), 400
    
    # In a real implementation, this would capture from camera
    # For now, return empty result
    return jsonify({
        'image': '',
        'detections': []
    }), 200

@detect_bp.route('/uploads/results/<filename>', methods=['GET'])
def get_result_file(filename):
    filepath = Config.UPLOAD_FOLDER / 'results' / filename
    if filepath.exists():
        return send_file(filepath)
    return jsonify({'message': 'File not found'}), 404

