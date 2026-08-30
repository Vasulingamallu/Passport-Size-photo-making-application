import os
import uuid
from PIL import Image, ImageOps
from flask import current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.photo import Photo

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

class UploadService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic'}
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in UploadService.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file(file):
        """Validates file type, size, and integrity."""
        if not file or not file.filename:
            return False, "No file provided."
            
        if not UploadService.allowed_file(file.filename):
            return False, "File type not allowed."
            
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > UploadService.MAX_FILE_SIZE:
            return False, "File size exceeds 20MB limit."
            
        try:
            img = Image.open(file)
            img.verify()  # Verify it's an image
            file.seek(0)  # Reset pointer after verify
        except Exception as e:
            file.seek(0)
            return False, f"Invalid or corrupted image file: {str(e)}"
            
        return True, "Valid"

    @staticmethod
    def generate_unique_filename(original_filename):
        """UUID + original extension"""
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        if ext == 'heic':
            ext = 'jpg'  # We convert HEIC to JPG
        return f"{uuid.uuid4().hex}.{ext}"

    @staticmethod
    def create_thumbnail(image_path, thumb_path, size=(200, 200)):
        """Create thumbnail using Pillow"""
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail(size)
                img.save(thumb_path, format="JPEG", quality=85)
            return True
        except Exception as e:
            current_app.logger.error(f"Error creating thumbnail: {str(e)}")
            return False

    @staticmethod
    def convert_heic_to_jpg(heic_path):
        """Convert HEIC to JPG"""
        try:
            new_path = heic_path.rsplit('.', 1)[0] + '.jpg'
            with Image.open(heic_path) as img:
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGB")
                img.save(new_path, format="JPEG", quality=95)
            os.remove(heic_path)
            return new_path
        except Exception as e:
            current_app.logger.error(f"Error converting HEIC: {str(e)}")
            return heic_path

    @staticmethod
    def get_image_info(file_path):
        """Return dict with width, height, format, mode, file_size"""
        info = {
            'width': 0, 'height': 0, 'format': '', 'mode': '', 'file_size': 0
        }
        if not os.path.exists(file_path):
            return info
            
        info['file_size'] = os.path.getsize(file_path)
        try:
            with Image.open(file_path) as img:
                info['width'] = img.width
                info['height'] = img.height
                info['format'] = img.format
                info['mode'] = img.mode
        except Exception as e:
            current_app.logger.error(f"Error getting image info: {str(e)}")
            
        return info

    @staticmethod
    def save_upload(file, user_id):
        """Save file, create thumbnail, create Photo DB record"""
        try:
            is_valid, msg = UploadService.validate_file(file)
            if not is_valid:
                raise ValueError(msg)

            original_filename = secure_filename(file.filename) if file.filename else ''
            if not original_filename:
                original_filename = f"photo_{uuid.uuid4().hex[:8]}.jpg"
            unique_filename = UploadService.generate_unique_filename(original_filename)
            
            base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            originals_dir = os.path.join(base_dir, 'originals')
            thumbs_dir = os.path.join(base_dir, 'thumbnails')
            
            os.makedirs(originals_dir, exist_ok=True)
            os.makedirs(thumbs_dir, exist_ok=True)
            
            # Save original file
            temp_filename = getattr(file, 'filename', 'photo.jpg') or 'photo.jpg'
            is_heic = temp_filename.lower().endswith('.heic')
            save_name = f"{uuid.uuid4().hex}.heic" if is_heic else unique_filename
            
            original_path = os.path.join(originals_dir, save_name)
            if hasattr(file, 'save'):
                file.save(original_path)
            else:
                file.seek(0)
                with open(original_path, 'wb') as f:
                    f.write(file.read())
            
            if is_heic:
                original_path = UploadService.convert_heic_to_jpg(original_path)
                unique_filename = os.path.basename(original_path)
            
            # Create thumbnail
            thumb_filename = f"thumb_{unique_filename}"
            thumb_path = os.path.join(thumbs_dir, thumb_filename)
            UploadService.create_thumbnail(original_path, thumb_path)
            
            # Get info
            info = UploadService.get_image_info(original_path)
            
            # Create DB record
            rel_original_path = f"originals/{unique_filename}"
            rel_thumb_path = f"thumbnails/{thumb_filename}"
            
            photo = Photo(
                user_id=user_id,
                original_filename=original_filename,
                original_path=rel_original_path,
                thumbnail_path=rel_thumb_path,
                file_size=info['file_size'],
                mime_type=getattr(file, 'mimetype', None) or getattr(file, 'content_type', None) or 'image/jpeg',
                status='uploaded'
            )
            
            db.session.add(photo)
            db.session.commit()
            
            return photo
            
        except Exception as e:
            current_app.logger.error(f"Error saving upload: {str(e)}")
            raise e
