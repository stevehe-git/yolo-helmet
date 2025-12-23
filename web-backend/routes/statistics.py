from flask import Blueprint, request, jsonify
from models import Detection, db
from utils.auth import login_required, admin_required
from sqlalchemy import func
from datetime import datetime, timedelta

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('', methods=['GET'])
@admin_required
def get_statistics():
    # Get total statistics
    total_detections = Detection.query.count()
    with_helmet = Detection.query.with_entities(func.sum(Detection.with_helmet)).scalar() or 0
    without_helmet = Detection.query.with_entities(func.sum(Detection.without_helmet)).scalar() or 0
    
    detection_rate = 0
    if total_detections > 0:
        total_people = with_helmet + without_helmet
        if total_people > 0:
            detection_rate = with_helmet / total_people
    
    # Get daily statistics for last 30 days
    daily_stats = []
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        count = Detection.query.filter(
            func.date(Detection.created_at) == date.date()
        ).count()
        daily_stats.append({'date': date_str, 'count': count})
    
    daily_stats.reverse()
    
    return jsonify({
        'total_detections': total_detections,
        'with_helmet': int(with_helmet),
        'without_helmet': int(without_helmet),
        'detection_rate': detection_rate,
        'daily_stats': daily_stats
    }), 200

@statistics_bp.route('/history', methods=['GET'])
@admin_required
def get_detection_history():
    days = request.args.get('days', 30, type=int)
    
    detections = Detection.query.filter(
        Detection.created_at >= datetime.now() - timedelta(days=days)
    ).order_by(Detection.created_at.desc()).limit(100).all()
    
    return jsonify([d.to_dict() for d in detections]), 200

