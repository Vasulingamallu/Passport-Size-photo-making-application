import os
import uuid
import mimetypes

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def get_file_size_formatted(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(os.math.floor(os.math.log(size_bytes, 1024)))
    p = os.math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def generate_unique_filename(original: str) -> str:
    ext = get_file_extension(original)
    return f"{uuid.uuid4().hex}{ext}"

def get_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'
