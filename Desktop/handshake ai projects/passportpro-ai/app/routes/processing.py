from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
import numpy as np

from app.extensions import db
from app.models.photo import Photo, PhotoJob
from app.services.face_service import FaceService
from app.services.background_service import BackgroundService
from app.services.enhancement_service import EnhancementService
from app.services.validation_service import ValidationService

bp = Blueprint('processing', __name__, url_prefix='/process')

def sanitize_for_json(obj):
    """Recursively convert NumPy data types to native Python types."""
    if isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]
    return obj

@bp.route('/<int:photo_id>/detect-face', methods=['POST'])
@login_required
def detect_face(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        service = FaceService()
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.original_path)
        result = sanitize_for_json(service.detect_and_analyze(image_path))
        
        photo.face_data = json.dumps(result)
        
        job = PhotoJob(photo_id=photo.id, job_type='face_detection', status='completed')
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:photo_id>/remove-background', methods=['POST'])
@login_required
def remove_background(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    bg_color = request.json.get('bg_color', '#FFFFFF') if request.is_json else '#FFFFFF'

    try:
        service = BackgroundService()
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.original_path)
        
        base_name = os.path.splitext(os.path.basename(photo.original_path))[0]
        processed_filename = f"{base_name}_processed.png"
        processed_rel_path = f"processed/{processed_filename}"
        processed_path = os.path.join(current_app.config['UPLOAD_FOLDER'], processed_rel_path)
        
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        service.remove_and_replace(input_path, processed_path, bg_color)
        
        photo.processed_path = processed_rel_path
        photo.status = 'processed'
        
        job = PhotoJob(photo_id=photo.id, job_type='background_removal', status='completed')
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'success': True, 'processed_url': f"/photos/{photo.id}/image/processed"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:photo_id>/enhance', methods=['POST'])
@login_required
def enhance(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    options = request.json.get('options', {}) if request.is_json else {}

    try:
        service = EnhancementService()
        source_path_rel = photo.processed_path if photo.processed_path else photo.original_path
        input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], source_path_rel)
        
        base_name = os.path.splitext(os.path.basename(source_path_rel))[0]
        ext = os.path.splitext(source_path_rel)[1] or '.jpg'
        enhanced_filename = f"{base_name}_enhanced{ext}"
        enhanced_rel_path = f"processed/{enhanced_filename}"
        enhanced_path = os.path.join(current_app.config['UPLOAD_FOLDER'], enhanced_rel_path)
        
        os.makedirs(os.path.dirname(enhanced_path), exist_ok=True)
        service.enhance_photo(input_path, enhanced_path, options)
        
        photo.processed_path = enhanced_rel_path
        photo.status = 'processed'
        
        job = PhotoJob(photo_id=photo.id, job_type='enhancement', status='completed')
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'success': True, 'processed_url': f"/photos/{photo.id}/image/processed"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:photo_id>/validate', methods=['POST'])
@login_required
def validate(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        service = ValidationService()
        source_path_rel = photo.processed_path if photo.processed_path else photo.original_path
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], source_path_rel)
        
        result = sanitize_for_json(service.validate_photo(image_path))
        
        photo.validation_score = result.get('total_score')
        
        job = PhotoJob(photo_id=photo.id, job_type='validation', status='completed')
        db.session.add(job)
        db.session.commit()
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:photo_id>/auto', methods=['POST'])
@login_required
def auto_process(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        input_path = os.path.join(upload_folder, photo.original_path)
        base_name = os.path.splitext(os.path.basename(photo.original_path))[0]
        
        processed_dir = os.path.join(upload_folder, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        face_service = FaceService()
        face_result = sanitize_for_json(face_service.detect_and_analyze(input_path))
        photo.face_data = json.dumps(face_result)
        
        bg_service = BackgroundService()
        auto_rel_path = f"processed/{base_name}_auto.png"
        auto_path = os.path.join(upload_folder, auto_rel_path)
        bg_service.remove_and_replace(input_path, auto_path, '#FFFFFF')
        
        enh_service = EnhancementService()
        auto_enh_rel_path = f"processed/{base_name}_auto_enh.png"
        auto_enh_path = os.path.join(upload_folder, auto_enh_rel_path)
        enh_service.auto_enhance(auto_path, auto_enh_path)
        
        photo.processed_path = auto_enh_rel_path
        photo.status = 'processed'
        
        val_service = ValidationService()
        val_result = sanitize_for_json(val_service.validate_photo(auto_enh_path))
        photo.validation_score = val_result.get('total_score')
        
        job = PhotoJob(photo_id=photo.id, job_type='auto_pipeline', status='completed')
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'processed_url': f"/photos/{photo.id}/image/processed",
            'validation': val_result,
            'face_data': face_result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
