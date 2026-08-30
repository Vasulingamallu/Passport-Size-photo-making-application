from datetime import datetime, timezone
from app.extensions import db

class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(255), nullable=False)
    processed_path = db.Column(db.String(255), nullable=True)
    thumbnail_path = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='uploaded')
    face_data = db.Column(db.Text, nullable=True)
    validation_score = db.Column(db.Integer, nullable=True)
    selected_country = db.Column(db.String(100), nullable=True)
    selected_document = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    jobs = db.relationship('PhotoJob', backref='photo', cascade='all, delete-orphan', lazy=True)

class PhotoJob(db.Model):
    __tablename__ = 'photo_jobs'

    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    result_data = db.Column(db.Text, nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
