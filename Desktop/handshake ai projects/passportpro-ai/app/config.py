"""
PassportPro AI - Application Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _get_database_uri() -> str:
    """Get database URI with fallback to SQLite and postgres fix for SQLAlchemy 2.0."""
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url or not db_url.strip():
        return f'sqlite:///{os.path.join(BASE_DIR, "passportpro.db")}'
    if db_url.startswith('postgres://'):
        return db_url.replace('postgres://', 'postgresql://', 1)
    return db_url


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _get_database_uri()

    # Upload settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 20 * 1024 * 1024))  # 20MB
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'uploads'))
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'heic'}

    # Upload subdirectories
    ORIGINALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'originals')
    PROCESSED_FOLDER = os.path.join(UPLOAD_FOLDER, 'processed')
    THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'temp')

    # AI settings
    FACE_DETECTION_CONFIDENCE = float(os.getenv('FACE_DETECTION_CONFIDENCE', 0.5))
    BACKGROUND_MODEL = os.getenv('BACKGROUND_MODEL', 'u2net')

    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@passportpro.ai')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme123')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app) if hasattr(Config, 'init_app') else None


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
