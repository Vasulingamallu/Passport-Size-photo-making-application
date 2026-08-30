"""
PassportPro AI - Application Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "passportpro.db")}'
    )


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')

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
