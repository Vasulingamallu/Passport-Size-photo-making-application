import os
import base64
import uuid
from io import BytesIO
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from app.extensions import db
from app.models.photo import Photo
from app.services.upload_service import UploadService
from app.services.storage_service import StorageService

bp = Blueprint('photos', __name__, url_prefix='/photos')

@bp.route('/')
@login_required
def gallery():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Photo.query.filter_by(user_id=current_user.id)
    if status != 'all':
        query = query.filter_by(status=status)
        
    pagination = query.order_by(Photo.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    photos = pagination.items
    return render_template('photo/gallery.html', photos=photos, pagination=pagination, current_status=status)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'No file part'}), 400
            flash('No file provided.', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'No selected file'}), 400
            flash('No selected file.', 'danger')
            return redirect(request.url)
            
        try:
            photo = UploadService.save_upload(file, current_user.id)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'photo_id': photo.id, 'redirect_url': url_for('photos.view', photo_id=photo.id)})
            flash('Photo uploaded successfully.', 'success')
            return redirect(url_for('photos.view', photo_id=photo.id))
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': str(e)}), 400
            flash(f'Error uploading photo: {str(e)}', 'danger')
            return redirect(request.url)
            
    return render_template('photo/upload.html')

@bp.route('/camera')
@login_required
def camera():
    return render_template('photo/camera.html')

@bp.route('/capture', methods=['POST'])
@login_required
def capture():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
        
    try:
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        file_obj = BytesIO(image_bytes)
        file_obj.filename = f"capture_{uuid.uuid4().hex[:8]}.jpg"
        file_obj.content_type = 'image/jpeg'
        
        photo = UploadService.save_upload(file_obj, current_user.id)
        return jsonify({'success': True, 'photo_id': photo.id, 'redirect_url': url_for('photos.view', photo_id=photo.id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:photo_id>')
@login_required
def view(photo_id):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('photo/view.html', photo=photo)

@bp.route('/<int:photo_id>/validation')
@login_required
def validation(photo_id):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('photo/validation.html', photo=photo)

@bp.route('/<int:photo_id>/background')
@login_required
def background(photo_id):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('photo/background.html', photo=photo)

@bp.route('/<int:photo_id>/enhance')
@login_required
def enhance(photo_id):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('photo/enhance.html', photo=photo)

@bp.route('/<int:photo_id>/passport')
@login_required
def passport(photo_id):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('photo/passport.html', photo=photo)

@bp.route('/<int:photo_id>/printsheet')
@login_required
def printsheet(photo_id):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    return render_template('photo/printsheet.html', photo=photo)

@bp.route('/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete(photo_id):
    from app.models.photo import PhotoJob
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    
    try:
        base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if photo.original_path:
            StorageService.delete_file(os.path.join(base_dir, photo.original_path))
        if photo.thumbnail_path:
            StorageService.delete_file(os.path.join(base_dir, photo.thumbnail_path))
        if photo.processed_path:
            StorageService.delete_file(os.path.join(base_dir, photo.processed_path))
            
        # Clean up related jobs
        PhotoJob.query.filter_by(photo_id=photo.id).delete()
        
        db.session.delete(photo)
        db.session.commit()
        flash('Photo deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting photo: {str(e)}', 'danger')
        
    return redirect(url_for('photos.gallery'))

@bp.route('/<int:photo_id>/image/<image_type>')
@login_required
def serve_image(photo_id, image_type):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    path_map = {
        'original': photo.original_path,
        'processed': photo.processed_path,
        'thumbnail': photo.thumbnail_path
    }
    
    rel_path = path_map.get(image_type)
    if not rel_path:
        return "Image not found", 404
        
    full_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(full_path):
        return "Image not found", 404
        
    return send_file(full_path)

@bp.route('/ai-studio')
@login_required
def ai_studio():
    from app.services.passport_service import PassportService
    passport_service = PassportService()
    countries = passport_service.get_all_countries()
    
    photo_id = request.args.get('photo_id', type=int)
    selected_photo = None
    if photo_id:
        selected_photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first()
        
    recent_photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.created_at.desc()).limit(6).all()
    
    return render_template('photo/ai_studio.html', 
                           countries=countries, 
                           selected_photo=selected_photo, 
                           recent_photos=recent_photos)

@bp.route('/ai-studio/generate', methods=['POST'])
@login_required
def ai_studio_generate():
    from app.services.ai_studio_service import AIStudioService
    import time
    
    try:
        photo = None
        # Check if new file was uploaded
        if 'file' in request.files and request.files['file'].filename != '':
            photo = UploadService.save_upload(request.files['file'], current_user.id)
        else:
            photo_id = request.form.get('photo_id') or (request.json.get('photo_id') if request.is_json else None)
            if photo_id:
                photo = Photo.query.filter_by(id=int(photo_id), user_id=current_user.id).first()
                
        if not photo:
            return jsonify({'error': 'No photo provided or selected'}), 400
            
        data = request.form if request.form else (request.json or {})
        
        country_code = data.get('country_code', 'US')
        document_type = data.get('document_type', 'Passport')
        bg_color = data.get('bg_color', '#FFFFFF')
        sheet_size = data.get('sheet_size', '4x6')
        photo_count = int(data.get('photo_count', 6))
        cutting_guides = str(data.get('cutting_guides', 'true')).lower() in ('true', '1', 'yes')
        custom_w = float(data.get('custom_w', 35.0))
        custom_h = float(data.get('custom_h', 45.0))
        custom_dpi = int(data.get('custom_dpi', 300))
        ai_provider = data.get('ai_provider', 'none')
        api_key = data.get('api_key', '')
        apply_enhancement = str(data.get('apply_enhancement', 'false')).lower() in ('true', '1', 'yes')
        remove_bg = str(data.get('remove_bg', 'true')).lower() in ('true', '1', 'yes')
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        processed_dir = os.path.join(upload_folder, 'processed')
        input_image_path = os.path.join(upload_folder, photo.original_path)
        
        studio = AIStudioService()
        result = studio.process_one_click(
            input_image_path=input_image_path,
            output_dir=processed_dir,
            file_prefix=str(photo.id),
            country_code=country_code,
            document_type=document_type,
            bg_color=bg_color,
            sheet_size=sheet_size,
            photo_count=photo_count,
            cutting_guides=cutting_guides,
            custom_w=custom_w,
            custom_h=custom_h,
            custom_dpi=custom_dpi,
            ai_provider=ai_provider,
            api_key=api_key,
            apply_enhancement=apply_enhancement,
            remove_bg=remove_bg
        )
        
        # Update photo state
        photo.processed_path = f"processed/passport_{photo.id}.jpg"
        photo.selected_country = country_code
        photo.selected_document = document_type
        photo.status = 'completed'
        db.session.commit()
        
        ts = int(time.time())
        return jsonify({
            'success': True,
            'photo_id': photo.id,
            'original_url': url_for('photos.serve_image', photo_id=photo.id, image_type='original'),
            'passport_url': f"/photos/{photo.id}/image/processed?t={ts}",
            'passport_download_url': url_for('downloads.download_photo', photo_id=photo.id),
            'printsheet_jpg_url': f"/download/printsheet/{photo.id}?sheet_size={sheet_size}&photo_count={photo_count}&format=jpg&t={ts}",
            'printsheet_pdf_url': f"/download/printsheet/{photo.id}?sheet_size={sheet_size}&photo_count={photo_count}&format=pdf&t={ts}",
            'dimension_label': result['dimension_label'],
            'sheet_info': result['sheet_info'],
            'cloud_ai': result.get('cloud_ai', {})
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

