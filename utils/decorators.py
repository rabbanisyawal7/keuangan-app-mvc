"""
DECORATORS & HELPER FUNCTIONS
"""
from functools import wraps
from flask import session, redirect, url_for, request
from werkzeug.utils import secure_filename
from config import Config
import os

def login_required(f):
    """
    Decorator untuk memastikan user sudah login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """
    Cek apakah file upload diperbolehkan
    Args:
        filename: nama file
    Returns: Boolean
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file, user_id):
    """
    Simpan file yang diupload
    Args:
        file: FileStorage object
        user_id: ID user
    Returns: URL path file atau None
    """
    if file and allowed_file(file.filename):
        from datetime import datetime
        
        # Buat nama file unik
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # Pastikan folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Simpan file
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Return URL path
        return f"/{Config.UPLOAD_FOLDER}/{filename}"
    
    return None

def format_currency(value):
    """
    Format angka menjadi format mata uang Indonesia
    Args:
        value: angka
    Returns: string format Rp
    """
    try:
        return f"Rp {float(value):,.0f}".replace(',', '.')
    except:
        return "Rp 0"

def get_current_user_id():
    """
    Dapatkan user_id dari session
    Returns: user_id atau None
    """
    return session.get('user_id')