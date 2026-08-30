import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import current_app

class StorageService:
    @staticmethod
    def save_file(file_data, folder, filename):
        """Save to specified folder, return full path"""
        base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        target_dir = os.path.join(base_dir, folder)
        os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, secure_filename(filename))
        file_data.save(file_path)
        return file_path
        
    @staticmethod
    def get_file_path(folder, filename):
        """Return absolute path"""
        base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        return os.path.abspath(os.path.join(base_dir, folder, filename))
        
    @staticmethod
    def delete_file(file_path):
        """Safely delete file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False
        
    @staticmethod
    def cleanup_temp():
        """Delete all files in temp folder older than 1 hour"""
        base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        temp_dir = os.path.join(base_dir, 'temp')
        
        if not os.path.exists(temp_dir):
            return 0
            
        count = 0
        cutoff = datetime.now() - timedelta(hours=1)
        
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff:
                    StorageService.delete_file(file_path)
                    count += 1
        return count
        
    @staticmethod
    def get_storage_stats():
        """Return dict with total_files, total_size, folder breakdown"""
        base_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        stats = {
            'total_files': 0,
            'total_size': 0,
            'folders': {}
        }
        
        if not os.path.exists(base_dir):
            return stats
            
        for root, dirs, files in os.walk(base_dir):
            folder_name = os.path.relpath(root, base_dir)
            if folder_name == '.':
                folder_name = 'root'
                
            folder_files = len(files)
            folder_size = sum(os.path.getsize(os.path.join(root, name)) for name in files)
            
            stats['folders'][folder_name] = {
                'files': folder_files,
                'size': folder_size
            }
            
            stats['total_files'] += folder_files
            stats['total_size'] += folder_size
            
        return stats
