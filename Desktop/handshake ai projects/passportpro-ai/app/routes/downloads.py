from flask import Blueprint, send_file, request, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.photo import Photo
from app.services.print_service import PrintService
import os

bp = Blueprint('downloads', __name__, url_prefix='/download')
print_service = PrintService()

@bp.route('/photo/<int:photo_id>', methods=['GET'])
@login_required
def download_photo(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id, user_id=current_user.id).first()
    if not photo:
        abort(404)
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # Try processed path first, then original
    rel_path = photo.processed_path or photo.original_path
    if not rel_path:
        abort(404)
    
    file_path = os.path.join(upload_folder, rel_path)
    if not os.path.exists(file_path):
        abort(404)
        
    return send_file(file_path, as_attachment=True)

@bp.route('/photo/<int:photo_id>/original', methods=['GET'])
@login_required
def download_original(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id, user_id=current_user.id).first()
    if not photo or not photo.original_path:
        abort(404)
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, photo.original_path)
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, as_attachment=True)

@bp.route('/printsheet/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def generate_printsheet(photo_id):
    photo = db.session.query(Photo).filter_by(id=photo_id, user_id=current_user.id).first()
    if not photo:
        abort(404)
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    rel_path = photo.processed_path or photo.original_path
    if not rel_path:
        abort(404)
    
    file_path = os.path.join(upload_folder, rel_path)
    if not os.path.exists(file_path):
        abort(404)
        
    if request.method == 'POST':
        data = request.json or {}
    else:
        data = request.args
        
    sheet_size = data.get('sheet_size', '4x6')
    photo_count = int(data.get('photo_count', 6))
    cutting_guides = str(data.get('cutting_guides', 'true')).lower() in ('true', '1', 'yes')
    fmt = data.get('format', data.get('fmt', 'jpg')).lower()
    
    ext = 'pdf' if fmt == 'pdf' else 'jpg'
    output_filename = f"printsheet_{photo.id}.{ext}"
    output_path = os.path.join(upload_folder, 'processed', output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        if fmt == 'pdf':
            print_service.generate_pdf_sheet(file_path, sheet_size, photo_count, output_path, cutting_guides)
        else:
            print_service.generate_print_sheet(file_path, sheet_size, photo_count, output_path, cutting_guides)
            
        return send_file(output_path, as_attachment=True, download_name=f"printsheet_{photo.id}_{sheet_size}.{ext}")
    except Exception as e:
        return str(e), 500
