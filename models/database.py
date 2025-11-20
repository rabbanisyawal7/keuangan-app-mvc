"""
DATABASE CONNECTION & INITIALIZATION
"""
import pymysql
from pymysql.cursors import DictCursor
from config import Config

def get_db_connection():
    """
    Membuat koneksi ke database MySQL
    Returns: pymysql connection object
    """
    return pymysql.connect(
        host=Config.DB_CONFIG['host'],
        user=Config.DB_CONFIG['user'],
        password=Config.DB_CONFIG['password'],
        database=Config.DB_CONFIG['database'],
        charset=Config.DB_CONFIG['charset'],
        cursorclass=DictCursor
    )

def init_database():
    """
    Inisialisasi database dan tabel-tabel yang dibutuhkan
    Returns: Boolean (True jika berhasil)
    """
    try:
        # Koneksi tanpa database untuk membuat database
        conn = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Buat database jika belum ada
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_CONFIG['database']}")
        cursor.execute(f"USE {Config.DB_CONFIG['database']}")
        
        # Cek dan buat tabel users
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    nama_lengkap VARCHAR(100),
                    tanggal_lahir DATE,
                    jenis_kelamin ENUM('Laki-laki', 'Perempuan', 'Lainnya'),
                    no_telepon VARCHAR(20),
                    alamat TEXT,
                    foto_profil VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                )
            """)
            print("✅ Tabel 'users' berhasil dibuat")
        
        # Cek dan buat tabel transaksi
        cursor.execute("SHOW TABLES LIKE 'transaksi'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE transaksi (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    tanggal DATE NOT NULL,
                    tipe VARCHAR(20) NOT NULL,
                    kategori VARCHAR(50) NOT NULL,
                    jumlah DECIMAL(15,2) NOT NULL,
                    keterangan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_tanggal (tanggal),
                    INDEX idx_tipe (tipe)
                )
            """)
            print("✅ Tabel 'transaksi' berhasil dibuat")
        
        # Cek dan buat tabel tabungan
        cursor.execute("SHOW TABLES LIKE 'tabungan'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE tabungan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT UNIQUE NOT NULL,
                    jumlah DECIMAL(15,2) DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id)
                )
            """)
            print("✅ Tabel 'tabungan' berhasil dibuat")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database berhasil diinisialisasi!")
        return True
        
    except Exception as e:
        print(f"❌ Error inisialisasi database: {e}")
        return False

def test_connection():
    """
    Test koneksi database
    Returns: Boolean
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Koneksi database gagal: {e}")
        return False