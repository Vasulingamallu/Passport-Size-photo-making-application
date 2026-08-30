from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.photo import Photo, PhotoJob

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def require_admin():
    from flask import redirect, url_for
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.role != 'admin':
        abort(403)

@bp.route('/')
def dashboard():
    total_users = db.session.query(User).count()
    total_photos = db.session.query(Photo).count()
    
    # Photos today
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    photos_today = db.session.query(Photo).filter(Photo.created_at >= today).count()
    
    # Mock storage
    storage_used = "1.5 GB"
    
    recent_jobs = db.session.query(PhotoJob).order_by(PhotoJob.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                           total_users=total_users,
                           total_photos=total_photos,
                           photos_today=photos_today,
                           storage_used=storage_used,
                           recent_jobs=recent_jobs)

@bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    users_paginated = db.session.query(User).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users_paginated)

@bp.route('/photos')
def photos():
    page = request.args.get('page', 1, type=int)
    photos_paginated = db.session.query(Photo).order_by(Photo.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/photos.html', photos=photos_paginated)

@bp.route('/stats')
def stats():
    return jsonify({"status": "ok"})
