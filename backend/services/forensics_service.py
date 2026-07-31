import hashlib
import os
from datetime import datetime

def generate_md5(file_path):
    """Generate MD5 hash for a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def generate_sha256(file_path):
    """Generate SHA256 hash for a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def extract_metadata(file_path, original_name):
    """Extract file metadata."""
    stat = os.stat(file_path)
    ext = os.path.splitext(original_name)[1].lower()
    
    metadata = {
        "original_name": original_name,
        "size_bytes": stat.st_size,
        "size_human": human_readable_size(stat.st_size),
        "extension": ext,
        "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
    }
    return metadata

def human_readable_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp',
    'txt', 'log', 'csv', 'doc', 'docx', 'xls',
    'xlsx', 'zip', 'tar', 'gz', 'json', 'xml', 'eml'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type_category(extension):
    ext = extension.lower().lstrip('.')
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
        return 'Image'
    elif ext == 'pdf':
        return 'PDF'
    elif ext in ['doc', 'docx']:
        return 'Document'
    elif ext in ['xls', 'xlsx', 'csv']:
        return 'Spreadsheet'
    elif ext in ['txt', 'log']:
        return 'Text/Log'
    elif ext in ['zip', 'tar', 'gz']:
        return 'Archive'
    elif ext in ['json', 'xml']:
        return 'Data'
    elif ext == 'eml':
        return 'Email'
    else:
        return 'Unknown'
