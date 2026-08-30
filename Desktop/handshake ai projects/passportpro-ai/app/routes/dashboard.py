from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.photo import Photo
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = current_user.id
    
    total_photos = db.session.query(Photo).filter_by(user_id=user_id).count()
    completed = db.session.query(Photo).filter_by(user_id=user_id, status='completed').count()
    
    # Photos this month
    now = datetime.utcnow()
    first_day = datetime(now.year, now.month, 1)
    this_month = db.session.query(Photo).filter(Photo.user_id == user_id, Photo.created_at >= first_day).count()
    
    recent_photos = db.session.query(Photo).filter_by(user_id=user_id).order_by(Photo.created_at.desc()).limit(5).all()
    
    # mock downloads
    downloads = 0
    
    return render_template('dashboard/index.html', 
                           total_photos=total_photos,
                           completed=completed,
                           this_month=this_month,
                           downloads=downloads,
                           recent_photos=recent_photos)
