from flask import Blueprint, jsonify, request, url_for, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.photo import Photo, PhotoJob
from app.services.passport_service import PassportService
from app.services.face_service import FaceService
import os
import json

bp = Blueprint('passport', __name__, url_prefix='/passport')
passport_service = PassportService()

@bp.route('/countries', methods=['GET'])
def get_countries():
    countries = passport_service.get_all_countries()
    return jsonify(countries)

@bp.route('/requirements/<country_code>', methods=['GET'])
def get_requirements(country_code):
    reqs = passport_service.get_country_requirements(country_code)
    return jsonify(reqs)

def _get_or_detect_face(photo, source_path):
    from app.utils.image_utils import load_image, save_image, straighten_face
    
    face_data = None
    face_info = None
    if photo.face_data and isinstance(photo.face_data, str):
        try:
            face_parsed = json.loads(photo.face_data)
            faces = face_parsed.get('detection', {}).get('faces', [])
            if faces:
                face_info = faces[0]
                bbox = face_info.get('bbox', {})
                face_data = {
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0),
                    'width': bbox.get('w', bbox.get('width', 0)),
                    'height': bbox.get('h', bbox.get('height', 0))
                }
        except Exception:
            pass

    if not face_data or face_data.get('width', 0) <= 0 or face_data.get('height', 0) <= 0:
        try:
            face_svc = FaceService()
            face_res = face_svc.detect_and_analyze(source_path)
            faces = face_res.get('detection', {}).get('faces', [])
            if faces:
                face_info = faces[0]
                bbox = face_info.get('bbox', {})
                face_data = {
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0),
                    'width': bbox.get('w', bbox.get('width', 0)),
                    'height': bbox.get('h', bbox.get('height', 0))
                }
                photo.face_data = json.dumps(face_res)
        except Exception:
            pass

    # Auto-straighten tilted posture if needed
    if face_info and os.path.exists(source_path):
        try:
            raw_img = load_image(source_path)
            if raw_img is not None:
                str_img, updated_info = straighten_face(raw_img, face_info)
                if updated_info.get('tilt_angle', 0.0) == 0.0:
                    save_image(str_img, source_path)
                    bbox = updated_info.get('bbox', {})
                    face_data = {
                        'x': bbox.get('x', 0),
                        'y': bbox.get('y', 0),
                        'width': bbox.get('w', bbox.get('width', 0)),
                        'height': bbox.get('h', bbox.get('height', 0))
                    }
        except Exception:
            pass

    if not face_data:
        face_data = {'x': 0, 'y': 0, 'width': 0, 'height': 0}
    return face_data

@bp.route('/<int:photo_id>/generate', methods=['POST'])
@login_required
def generate(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id, user_id=current_user.id).first()
    if not photo:
        abort(404)
        
    data = request.json or {}
    country_code = data.get('country_code')
    document_type = data.get('document_type')
    
    if not country_code or not document_type:
        return jsonify({'error': 'Missing parameters'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    processed_dir = os.path.join(upload_folder, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    output_filename = f"passport_{photo.id}.jpg"
    output_rel_path = f"processed/{output_filename}"
    output_path = os.path.join(upload_folder, output_rel_path)
    
    source_path = os.path.join(upload_folder, photo.processed_path if photo.processed_path else photo.original_path)
    
    try:
        face_data = _get_or_detect_face(photo, source_path)
        passport_service.generate_passport_photo(source_path, face_data, country_code, document_type, output_path)
        
        job = PhotoJob(photo_id=photo.id, job_type='passport_generation', status='completed')
        db.session.add(job)
        photo.processed_path = output_rel_path
        photo.selected_country = country_code
        photo.selected_document = document_type
        photo.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'download_url': url_for('downloads.download_photo', photo_id=photo.id),
            'processed_url': f"/photos/{photo.id}/image/processed"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:photo_id>/custom', methods=['POST'])
@login_required
def generate_custom(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id, user_id=current_user.id).first()
    if not photo:
        abort(404)
        
    data = request.json or {}
    width_mm = float(data.get('width_mm', 35))
    height_mm = float(data.get('height_mm', 45))
    dpi = int(data.get('dpi', 300))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    processed_dir = os.path.join(upload_folder, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    output_filename = f"custom_{photo.id}.jpg"
    output_rel_path = f"processed/{output_filename}"
    output_path = os.path.join(upload_folder, output_rel_path)
    
    source_path = os.path.join(upload_folder, photo.processed_path if photo.processed_path else photo.original_path)
    
    try:
        face_data = _get_or_detect_face(photo, source_path)
        passport_service.generate_custom_size(source_path, face_data, width_mm, height_mm, dpi, output_path)
        
        job = PhotoJob(photo_id=photo.id, job_type='custom_generation', status='completed')
        db.session.add(job)
        photo.processed_path = output_rel_path
        photo.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'download_url': url_for('downloads.download_photo', photo_id=photo.id),
            'processed_url': f"/photos/{photo.id}/image/processed"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
