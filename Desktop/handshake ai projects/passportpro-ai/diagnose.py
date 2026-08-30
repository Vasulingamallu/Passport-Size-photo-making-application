"""Quick diagnostic to check if PassportPro AI can start."""
import sys
import os

# Set the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

print(f"Python: {sys.version}")
print(f"Project: {project_root}")
print()

# Check required packages
packages = [
    'flask', 'flask_sqlalchemy', 'flask_migrate', 'flask_login', 
    'flask_wtf', 'dotenv', 'werkzeug', 'PIL', 'cv2', 'numpy', 'fpdf2'
]

missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} - MISSING")
        missing.append(pkg)

print()
if missing:
    print(f"MISSING PACKAGES: {missing}")
    print("Run: pip install flask flask-sqlalchemy flask-migrate flask-login flask-wtf python-dotenv Pillow opencv-python-headless numpy fpdf2 waitress email-validator")
    sys.exit(1)

# Try to create the app
print("Creating Flask app...")
try:
    from app import create_app
    app = create_app('development')
    print("✓ App created successfully!")
    print(f"  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')}")
    print(f"  Upload folder: {app.config.get('UPLOAD_FOLDER', 'N/A')}")
    
    # List routes
    print("\nRegistered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        print(f"  {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    print("\n✓ Ready to run! Use: python run.py")
except Exception as e:
    print(f"✗ Error creating app: {e}")
    import traceback
    traceback.print_exc()
