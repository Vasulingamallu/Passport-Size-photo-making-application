"""
PassportPro AI - Flask Extensions

All Flask extensions are initialized here and imported into the app factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Database ORM
db = SQLAlchemy()

# Database migrations
migrate = Migrate()

# User session management
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# CSRF protection
csrf = CSRFProtect()
