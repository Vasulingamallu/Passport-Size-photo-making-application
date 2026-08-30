"""
PassportPro AI - Application Factory

Creates and configures the Flask application instance.
"""

import os
import logging
from importlib import import_module
Flask = import_module('flask').Flask
from .config import config_map
from .extensions import db, migrate, login_manager, csrf


def create_app(config_name: str = 'default') -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_map.get(config_name, config_map['default']))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Create upload directories
    _create_upload_dirs(app)

    # Configure logging
    _configure_logging(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Create database tables and seed data
    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
        _seed_data(app)

    return app


def _create_upload_dirs(app: Flask) -> None:
    """Create upload directories if they don't exist."""
    dirs = [
        app.config['UPLOAD_FOLDER'],
        app.config['ORIGINALS_FOLDER'],
        app.config['PROCESSED_FOLDER'],
        app.config['THUMBNAILS_FOLDER'],
        app.config['TEMP_FOLDER'],
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def _configure_logging(app: Flask) -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    app.logger.setLevel(log_level)


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from .routes.auth import bp as auth_bp
    from .routes.dashboard import bp as dashboard_bp
    from .routes.photos import bp as photos_bp
    from .routes.processing import bp as processing_bp
    from .routes.passport import bp as passport_bp
    from .routes.downloads import bp as downloads_bp
    from .routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(photos_bp)
    app.register_blueprint(processing_bp)
    app.register_blueprint(passport_bp)
    app.register_blueprint(downloads_bp)
    app.register_blueprint(admin_bp)

    # Register main/index route
    from flask import render_template as rt, redirect, url_for
    from flask_login import current_user

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return rt('index.html')


def _register_error_handlers(app: Flask) -> None:
    """Register custom error handlers."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def too_large(error):
        return render_template('errors/413.html'), 413


def _seed_data(app: Flask) -> None:
    """Seed initial data (country requirements, admin user)."""
    from .models.country import CountryRequirement
    from .models.user import User

    # Seed country requirements if empty
    if CountryRequirement.query.count() == 0:
        _seed_country_requirements()

    # Create admin user if not exists
    admin_email = app.config.get('ADMIN_EMAIL')
    if admin_email and not User.query.filter_by(email=admin_email).first():
        admin = User(
            name='Admin',
            email=admin_email,
            role='admin',
        )
        admin.set_password(app.config.get('ADMIN_PASSWORD', 'changeme123'))
        db.session.add(admin)
        db.session.commit()


def _seed_country_requirements() -> None:
    """Seed country/document photo requirements."""
    import json

    data_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'data', 'country_requirements.json'
    )
    if not os.path.exists(data_file):
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        requirements = json.load(f)

    from .models.country import CountryRequirement

    for req in requirements:
        record = CountryRequirement(
            country_name=req['country_name'],
            country_code=req['country_code'],
            document_type=req['document_type'],
            width_mm=req['width_mm'],
            height_mm=req['height_mm'],
            dpi=req.get('dpi', 300),
            background_color=req.get('background_color', '#FFFFFF'),
            head_size_min=req.get('head_size_min', 50),
            head_size_max=req.get('head_size_max', 80),
            notes=req.get('notes', ''),
        )
        db.session.add(record)
    db.session.commit()
