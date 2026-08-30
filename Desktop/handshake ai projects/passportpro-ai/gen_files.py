import os

base = r"c:\Users\linga\Desktop\handshake ai projects\passportpro-ai"

files = {
    r"app\templates\base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PassportPro AI{% endblock %}</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light custom-navbar sticky-top">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="{{ url_for('main.index') if current_user.is_authenticated else '/' }}">
                <i class="bi bi-camera-fill text-primary me-2"></i>
                <span class="fw-bold">PassportPro AI</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.index') if current_user.is_authenticated else '/' }}">Home</a>
                    </li>
                    {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <a class="nav-link" href="#">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Upload</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Camera</a>
                    </li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            {{ current_user.name }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="{{ url_for('auth.profile') }}">Profile</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">Logout</a></li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="btn btn-primary ms-2" href="{{ url_for('auth.register') }}">Register</a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0">&copy; {{ config.get('CURRENT_YEAR', '2024') }} PassportPro AI. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>""",

    r"app\templates\index.html": """{% extends "base.html" %}

{% block title %}PassportPro AI - Professional Passport Photos{% endblock %}

{% block content %}
<div class="hero-section text-center py-5 mb-5 bg-gradient">
    <div class="container py-5">
        <h1 class="display-4 fw-bold mb-4">Professional AI-Powered Passport Photos</h1>
        <p class="lead mb-4">Create perfect, compliant passport and visa photos from your home. Our AI handles the background, lighting, and sizing.</p>
        <div class="d-flex justify-content-center gap-3">
            <a href="{{ url_for('auth.register') }}" class="btn btn-primary btn-lg">Get Started</a>
            <a href="#" class="btn btn-outline-primary btn-lg bg-white">Upload Photo</a>
        </div>
    </div>
</div>

<div class="container mb-5">
    <h2 class="text-center fw-bold mb-5">Features</h2>
    <div class="row g-4">
        <div class="col-md-4">
            <div class="card h-100 feature-card text-center p-4">
                <i class="bi bi-camera text-primary display-4 mb-3"></i>
                <h4>Camera Capture</h4>
                <p class="text-muted">Take photos directly using your webcam or smartphone camera with guided overlays.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 feature-card text-center p-4">
                <i class="bi bi-person-bounding-box text-primary display-4 mb-3"></i>
                <h4>AI Background Removal</h4>
                <p class="text-muted">Automatically remove distracting backgrounds and replace with compliant solid colors.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 feature-card text-center p-4">
                <i class="bi bi-magic text-primary display-4 mb-3"></i>
                <h4>Photo Enhancement</h4>
                <p class="text-muted">Enhance lighting, contrast, and sharpness for professional-quality results.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 feature-card text-center p-4">
                <i class="bi bi-check-circle text-primary display-4 mb-3"></i>
                <h4>Quality Validation</h4>
                <p class="text-muted">Instant validation against ICAO standards for head size, positioning, and quality.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 feature-card text-center p-4">
                <i class="bi bi-aspect-ratio text-primary display-4 mb-3"></i>
                <h4>Multi-Size Generator</h4>
                <p class="text-muted">Generate exact sizes for passports and visas for over 100+ countries.</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100 feature-card text-center p-4">
                <i class="bi bi-printer text-primary display-4 mb-3"></i>
                <h4>Print Sheets</h4>
                <p class="text-muted">Generate ready-to-print 4x6 layouts with multiple photos for easy printing.</p>
            </div>
        </div>
    </div>
</div>

<div class="container mb-5">
    <h2 class="text-center fw-bold mb-5">How It Works</h2>
    <div class="row text-center g-4">
        <div class="col-md-3">
            <div class="fs-1 fw-bold text-primary mb-2">1</div>
            <i class="bi bi-upload fs-1 mb-3 d-block text-secondary"></i>
            <h5>Upload or Capture</h5>
            <p class="text-muted">Take a photo or upload an existing one.</p>
        </div>
        <div class="col-md-3">
            <div class="fs-1 fw-bold text-primary mb-2">2</div>
            <i class="bi bi-cpu fs-1 mb-3 d-block text-secondary"></i>
            <h5>AI Processing</h5>
            <p class="text-muted">Our AI removes the background and adjusts lighting.</p>
        </div>
        <div class="col-md-3">
            <div class="fs-1 fw-bold text-primary mb-2">3</div>
            <i class="bi bi-globe fs-1 mb-3 d-block text-secondary"></i>
            <h5>Select Country</h5>
            <p class="text-muted">Choose your target document and country.</p>
        </div>
        <div class="col-md-3">
            <div class="fs-1 fw-bold text-primary mb-2">4</div>
            <i class="bi bi-download fs-1 mb-3 d-block text-secondary"></i>
            <h5>Download</h5>
            <p class="text-muted">Get your perfectly formatted photos instantly.</p>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\templates\auth\login.html": """{% extends "base.html" %}

{% block title %}Login - PassportPro AI{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow-sm auth-card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="bi bi-camera-fill text-primary display-4"></i>
                        <h2 class="fw-bold mt-2">Welcome Back</h2>
                        <p class="text-muted">Login to PassportPro AI</p>
                    </div>
                    
                    <form method="POST" action="{{ url_for('auth.login') }}">
                        <div class="form-floating mb-3">
                            <input type="email" class="form-control" id="email" name="email" placeholder="name@example.com" required>
                            <label for="email">Email address</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                            <label for="password">Password</label>
                        </div>
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember" name="remember">
                            <label class="form-check-label" for="remember">Remember me</label>
                        </div>
                        <button class="btn btn-primary w-100 py-2 mb-3" type="submit">Login</button>
                        <div class="text-center">
                            <p class="mb-0">Don't have an account? <a href="{{ url_for('auth.register') }}" class="text-decoration-none">Register</a></p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\templates\auth\register.html": """{% extends "base.html" %}

{% block title %}Register - PassportPro AI{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            <div class="card shadow-sm auth-card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="bi bi-camera-fill text-primary display-4"></i>
                        <h2 class="fw-bold mt-2">Create Account</h2>
                        <p class="text-muted">Join PassportPro AI</p>
                    </div>
                    
                    <form method="POST" action="{{ url_for('auth.register') }}">
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="name" name="name" placeholder="John Doe" required>
                            <label for="name">Full Name</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input type="email" class="form-control" id="email" name="email" placeholder="name@example.com" required>
                            <label for="email">Email address</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input type="password" class="form-control" id="password" name="password" placeholder="Password" required minlength="6">
                            <label for="password">Password</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="password" class="form-control" id="confirm_password" name="confirm_password" placeholder="Confirm Password" required minlength="6">
                            <label for="confirm_password">Confirm Password</label>
                        </div>
                        <button class="btn btn-primary w-100 py-2 mb-3" type="submit">Register</button>
                        <div class="text-center">
                            <p class="mb-0">Already have an account? <a href="{{ url_for('auth.login') }}" class="text-decoration-none">Login</a></p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\templates\auth\profile.html": """{% extends "base.html" %}

{% block title %}Profile - PassportPro AI{% endblock %}

{% block content %}
<div class="container py-4">
    <h2 class="fw-bold mb-4">My Profile</h2>
    <div class="row g-4">
        <div class="col-md-4">
            <div class="card shadow-sm text-center p-4 mb-4">
                <div class="mb-3">
                    <i class="bi bi-person-circle display-1 text-secondary"></i>
                </div>
                <h4 class="mb-1">{{ current_user.name }}</h4>
                <p class="text-muted mb-2">{{ current_user.email }}</p>
                <div class="mb-3">
                    <span class="badge bg-primary">{{ current_user.role|capitalize }}</span>
                </div>
                <p class="small text-muted mb-0">Member since {{ current_user.created_at.strftime('%Y-%m-%d') if current_user.created_at else 'Unknown' }}</p>
            </div>
            
            <div class="card shadow-sm p-4">
                <h5 class="card-title fw-bold mb-3">Photo Statistics</h5>
                <div class="d-flex justify-content-between mb-2">
                    <span>Total Photos:</span>
                    <span class="fw-bold">{{ current_user.photos|length if current_user.photos else 0 }}</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Downloads:</span>
                    <span class="fw-bold">0</span>
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card shadow-sm p-4 mb-4">
                <h5 class="card-title fw-bold mb-4">Edit Profile</h5>
                <form method="POST" action="{{ url_for('auth.profile') }}">
                    <div class="mb-3">
                        <label for="name" class="form-label">Full Name</label>
                        <input type="text" class="form-control" id="name" name="name" value="{{ current_user.name }}" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email Address</label>
                        <input type="email" class="form-control" id="email" name="email" value="{{ current_user.email }}" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </form>
            </div>
            
            <div class="card shadow-sm p-4">
                <h5 class="card-title fw-bold mb-4 text-danger">Change Password</h5>
                <form>
                    <div class="mb-3">
                        <label for="current_password" class="form-label">Current Password</label>
                        <input type="password" class="form-control" id="current_password">
                    </div>
                    <div class="mb-3">
                        <label for="new_password" class="form-label">New Password</label>
                        <input type="password" class="form-control" id="new_password">
                    </div>
                    <button type="button" class="btn btn-outline-danger disabled">Update Password (Coming Soon)</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\templates\errors\404.html": """{% extends "base.html" %}

{% block title %}404 - Page Not Found{% endblock %}

{% block content %}
<div class="container py-5 text-center">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <h1 class="display-1 fw-bold text-primary mb-4">404</h1>
            <h2 class="mb-4">Page Not Found</h2>
            <p class="text-muted mb-4">The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.</p>
            <a href="{{ url_for('main.index') }}" class="btn btn-primary">Go to Homepage</a>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\templates\errors\500.html": """{% extends "base.html" %}

{% block title %}500 - Internal Server Error{% endblock %}

{% block content %}
<div class="container py-5 text-center">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <h1 class="display-1 fw-bold text-danger mb-4">500</h1>
            <h2 class="mb-4">Internal Server Error</h2>
            <p class="text-muted mb-4">Oops! Something went wrong on our end. Please try again later.</p>
            <a href="{{ url_for('main.index') }}" class="btn btn-primary">Go to Homepage</a>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\templates\errors\413.html": """{% extends "base.html" %}

{% block title %}413 - File Too Large{% endblock %}

{% block content %}
<div class="container py-5 text-center">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <h1 class="display-1 fw-bold text-warning mb-4"><i class="bi bi-file-earmark-x"></i></h1>
            <h2 class="mb-4">File Too Large</h2>
            <p class="text-muted mb-4">The file you tried to upload exceeds the maximum allowed size. Please choose a smaller file (max 10MB).</p>
            <a href="{{ url_for('main.index') }}" class="btn btn-primary">Go Back</a>
        </div>
    </div>
</div>
{% endblock %}""",

    r"app\static\css\style.css": """:root {
    --primary: #1a237e;
    --primary-light: #3949ab;
    --secondary: #00bcd4;
    --accent: #ff6f00;
    --body-bg: #f8f9fa;
    --text-color: #333333;
}

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--body-bg);
    color: var(--text-color);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

main {
    flex: 1;
}

.custom-navbar {
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.text-primary {
    color: var(--primary) !important;
}

.btn-primary {
    background-color: var(--primary);
    border-color: var(--primary);
}

.btn-primary:hover {
    background-color: var(--primary-light);
    border-color: var(--primary-light);
}

.bg-gradient {
    background: linear-gradient(135deg, rgba(26,35,126,0.1) 0%, rgba(0,188,212,0.1) 100%);
}

.feature-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.auth-card {
    border-radius: 1rem;
    border: none;
}

.upload-zone {
    border: 2px dashed #ccc;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    background-color: #fff;
    cursor: pointer;
    transition: all 0.3s ease;
}

.upload-zone:hover {
    border-color: var(--primary);
    background-color: rgba(26,35,126,0.02);
}

.camera-container {
    background: #000;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
    min-height: 300px;
}

.score-display {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    color: white;
}

.score-good { background-color: #28a745; }
.score-warn { background-color: #ffc107; color: #000; }
.score-poor { background-color: #dc3545; }

.compare-slider {
    position: relative;
    overflow: hidden;
    border-radius: 10px;
}

.print-preview {
    background: white;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    margin: 0 auto;
}

@media (max-width: 768px) {
    .hero-section {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }
}
""",

    r"app\static\js\main.js": """document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(msg);
            bsAlert.close();
        }, 5000);
    });
});

const utils = {
    showSpinner: function(elementId) {
        const el = document.getElementById(elementId);
        if(el) {
            el.innerHTML = '<div class="spinner-border spinner-border-sm text-light" role="status"><span class="visually-hidden">Loading...</span></div>';
            el.disabled = true;
        }
    },
    
    hideSpinner: function(elementId, originalText) {
        const el = document.getElementById(elementId);
        if(el) {
            el.innerHTML = originalText;
            el.disabled = false;
        }
    },

    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    showToast: function(message, type = 'info') {
        console.log(`[${type}] ${message}`);
    },

    previewImage: function(input, previewElementId) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById(previewElementId);
                if(preview) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
            }
            reader.readAsDataURL(input.files[0]);
        }
    },
    
    confirmAction: function(message) {
        return confirm(message);
    }
};
""",
    r"app\models\__init__.py": """from app.models.user import User
from app.models.photo import Photo, PhotoJob
from app.models.country import CountryRequirement

__all__ = ['User', 'Photo', 'PhotoJob', 'CountryRequirement']
""",
    r"app\models\user.py": """from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    photos = db.relationship('Photo', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
""",
    r"app\models\photo.py": """from datetime import datetime, timezone
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

    jobs = db.relationship('PhotoJob', backref='photo', lazy=True)

class PhotoJob(db.Model):
    __tablename__ = 'photo_jobs'

    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    result_data = db.Column(db.Text, nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
""",
    r"app\models\country.py": """from app.extensions import db

class CountryRequirement(db.Model):
    __tablename__ = 'country_requirements'

    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    width_mm = db.Column(db.Float, nullable=False)
    height_mm = db.Column(db.Float, nullable=False)
    dpi = db.Column(db.Integer, default=300)
    background_color = db.Column(db.String(20), default='#FFFFFF')
    head_size_min = db.Column(db.Integer, default=50)
    head_size_max = db.Column(db.Integer, default=80)
    notes = db.Column(db.Text, nullable=True)
""",
    r"data\country_requirements.json": """[
  {"country_name": "India", "country_code": "IN", "document_type": "Passport", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 70, "head_size_max": 80, "notes": "White background, no glasses"},
  {"country_name": "India", "country_code": "IN", "document_type": "PAN Card", "width_mm": 25.0, "height_mm": 35.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 50, "head_size_max": 80, "notes": ""},
  {"country_name": "India", "country_code": "IN", "document_type": "Driving License", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 50, "head_size_max": 80, "notes": ""},
  {"country_name": "India", "country_code": "IN", "document_type": "Visa", "width_mm": 51.0, "height_mm": 51.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 50, "head_size_max": 80, "notes": ""},
  {"country_name": "India", "country_code": "IN", "document_type": "Aadhaar", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 50, "head_size_max": 80, "notes": ""},
  {"country_name": "USA", "country_code": "US", "document_type": "Passport", "width_mm": 51.0, "height_mm": 51.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 50, "head_size_max": 69, "notes": "2x2 inches"},
  {"country_name": "USA", "country_code": "US", "document_type": "Visa", "width_mm": 51.0, "height_mm": 51.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 50, "head_size_max": 69, "notes": "2x2 inches"},
  {"country_name": "United Kingdom", "country_code": "GB", "document_type": "Passport", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#E5E5E5", "head_size_min": 64, "head_size_max": 75, "notes": "Light grey or cream background"},
  {"country_name": "Canada", "country_code": "CA", "document_type": "Passport", "width_mm": 50.0, "height_mm": 70.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 44, "head_size_max": 51, "notes": ""},
  {"country_name": "Australia", "country_code": "AU", "document_type": "Passport", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 71, "head_size_max": 80, "notes": "White or light grey background"},
  {"country_name": "Schengen/EU", "country_code": "EU", "document_type": "Visa", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 70, "head_size_max": 80, "notes": "Light grey or white background"},
  {"country_name": "China", "country_code": "CN", "document_type": "Passport", "width_mm": 33.0, "height_mm": 48.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 58, "head_size_max": 68, "notes": "White background"},
  {"country_name": "Japan", "country_code": "JP", "document_type": "Passport", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 71, "head_size_max": 80, "notes": ""},
  {"country_name": "UAE", "country_code": "AE", "document_type": "Passport", "width_mm": 43.0, "height_mm": 55.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 70, "head_size_max": 80, "notes": ""},
  {"country_name": "Germany", "country_code": "DE", "document_type": "Passport", "width_mm": 35.0, "height_mm": 45.0, "dpi": 300, "background_color": "#FFFFFF", "head_size_min": 70, "head_size_max": 80, "notes": ""}
]
""",
    r"app\routes\__init__.py": "",
    r"app\routes\auth.py": """from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.register'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.index'))

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        if name and email:
            current_user.name = name
            current_user.email = email
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        else:
            flash('Name and email cannot be empty.', 'danger')
            
    return render_template('auth/profile.html')
"""
}

for rel_path, content in files.items():
    p = os.path.join(base, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
print("SUCCESS")
