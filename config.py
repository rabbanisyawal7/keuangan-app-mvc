"""
KONFIGURASI APLIKASI KEUANGAN MVC
"""
import os

class Config:
    """Konfigurasi utama aplikasi"""
    
    # Flask Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'keuangan_app_secret_key_2024'
    
    # Database Configuration
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST') or 'localhost',
        'user': os.environ.get('DB_USER') or 'root',
        'password': os.environ.get('DB_PASSWORD') or '',
        'database': os.environ.get('DB_NAME') or 'keuangan_db',
        'charset': 'utf8mb4',
    }
    
    # Upload Configuration
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    
    # Flask Configuration
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Kategori Transaksi
    KATEGORI_PEMASUKAN = ['Gaji', 'Hibah', 'Lainnya']
    KATEGORI_PENGELUARAN = ['Jajan', 'Transportasi', 'Makan', 'Kebutuhan', 'Keinginan', 'Lainnya']
    
    # Date Limits (untuk input transaksi)
    TRANSAKSI_DATE_RANGE_DAYS = 7  # ±7 hari dari hari ini
