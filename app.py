"""
APLIKASI PENCATAT KEUANGAN DENGAN FLASK & MYSQL
VERSI 4.1 - PERBAIKAN LOGIKA & UI

INSTALASI:
1. Install dependencies:
   pip install flask flask-cors pymysql pandas werkzeug pillow

2. Aktifkan XAMPP (Apache + MySQL)

3. Jalankan aplikasi:
   python app.py

4. Akses di browser:
   http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql
import pandas as pd
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'keuangan_app_secret_key_2024'
CORS(app)

# Konfigurasi upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Konfigurasi Database MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'keuangan_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS keuangan_db")
        cursor.execute("USE keuangan_db")
        
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_exists = cursor.fetchone()
        
        if not users_exists:
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'transaksi'")
        transaksi_exists = cursor.fetchone()
        
        if not transaksi_exists:
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
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        
        cursor.execute("SHOW TABLES LIKE 'tabungan'")
        tabungan_exists = cursor.fetchone()
        
        if not tabungan_exists:
            cursor.execute("""
                CREATE TABLE tabungan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT UNIQUE NOT NULL,
                    jumlah DECIMAL(15,2) DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database berhasil diinisialisasi!")
        return True
    except Exception as e:
        print(f"❌ Error inisialisasi database: {e}")
        return False

# Template HTML Login
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Aplikasi Keuangan</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        body {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 450px;
            width: 100%;
        }
        .logo {
            text-align: center;
            font-size: 60px;
            margin-bottom: 20px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            border: none;
            padding: 12px;
            border-radius: 10px;
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
        }
        .form-control:focus {
            border-color: #2ecc71;
            box-shadow: 0 0 0 0.2rem rgba(46, 204, 113, 0.25);
        }
        a { color: #2ecc71; }
        a:hover { color: #27ae60; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">💰</div>
        <h2 class="text-center mb-4">{{ title }}</h2>
        
        {% if error %}
        <div class="alert alert-danger">{{ error }}</div>
        {% endif %}
        
        {% if success %}
        <div class="alert alert-success">{{ success }}</div>
        {% endif %}
        
        <form method="POST">
            {% if is_register %}
            <div class="mb-3">
                <label class="form-label"><i class="bi bi-person"></i> Username</label>
                <input type="text" class="form-control" name="username" required>
            </div>
            <div class="mb-3">
                <label class="form-label"><i class="bi bi-envelope"></i> Email</label>
                <input type="email" class="form-control" name="email" required>
            </div>
            <div class="mb-3">
                <label class="form-label"><i class="bi bi-lock"></i> Password</label>
                <input type="password" class="form-control" name="password" required minlength="6">
            </div>
            <div class="mb-3">
                <label class="form-label"><i class="bi bi-lock-fill"></i> Konfirmasi Password</label>
                <input type="password" class="form-control" name="confirm_password" required minlength="6">
            </div>
            <button type="submit" class="btn btn-primary w-100">
                <i class="bi bi-person-plus"></i> Daftar Sekarang
            </button>
            <div class="text-center mt-3">
                <p>Sudah punya akun? <a href="/login">Login di sini</a></p>
            </div>
            {% else %}
            <div class="mb-3">
                <label class="form-label"><i class="bi bi-person"></i> Username atau Email</label>
                <input type="text" class="form-control" name="username" required>
            </div>
            <div class="mb-3">
                <label class="form-label"><i class="bi bi-lock"></i> Password</label>
                <input type="password" class="form-control" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">
                <i class="bi bi-box-arrow-in-right"></i> Login
            </button>
            <div class="text-center mt-3">
                <p>Belum punya akun? <a href="/register">Daftar sekarang</a></p>
            </div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

# Template HTML Aplikasi Utama
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Pencatat Keuangan Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --primary: #2ecc71;
            --primary-dark: #27ae60;
            --secondary: #f1c40f;
            --secondary-dark: #f39c12;
            --sidebar-width: 260px;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
            margin: 0;
            padding: 0;
        }
        
        /* Sidebar Desktop */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: var(--sidebar-width);
            height: 100vh;
            background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 20px 0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            overflow-y: auto;
            z-index: 1000;
            transition: transform 0.3s ease;
        }
        
        .sidebar .logo {
            text-align: center;
            color: white;
            font-size: 40px;
            margin-bottom: 10px;
        }
        
        .sidebar .brand {
            text-align: center;
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        
        .sidebar .user-info {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin: 0 15px 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
        }
        
        .sidebar .user-avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 12px;
            border: 2px solid white;
        }
        
        .sidebar .user-name {
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        
        .sidebar .user-email {
            color: rgba(255,255,255,0.8);
            font-size: 12px;
        }
        
        .sidebar .nav-link {
            color: white;
            padding: 12px 25px;
            margin: 5px 15px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .sidebar .nav-link:hover {
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }
        
        .sidebar .nav-link.active {
            background: white;
            color: var(--primary);
            font-weight: bold;
        }
        
        .sidebar .nav-link i {
            margin-right: 10px;
            font-size: 18px;
        }
        
        .sidebar .logout-btn {
            position: absolute;
            bottom: 20px;
            left: 15px;
            right: 15px;
            background: var(--secondary);
            color: #333;
            border: none;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .sidebar .logout-btn:hover {
            background: var(--secondary-dark);
        }
        
        /* Main Content */
        .main-content {
            margin-left: var(--sidebar-width);
            padding: 30px;
            min-height: 100vh;
        }
        
        .content-wrapper {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        /* Mobile Menu Toggle */
        .mobile-menu-toggle {
            display: none;
            position: fixed;
            top: 15px;
            left: 15px;
            z-index: 1100;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 24px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            cursor: pointer;
        }
        
        .mobile-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
        
        /* Buttons */
        .btn-primary {
            background: var(--primary);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        
        .btn-warning {
            background: var(--secondary);
            border: none;
            color: #333;
            border-radius: 8px;
        }
        
        .btn-warning:hover {
            background: var(--secondary-dark);
        }
        
        /* Stats Boxes */
        .stats-box {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
        }
        
        .stats-box h6 {
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .stats-box h3 {
            font-size: 20px;
            margin: 0;
        }
        
        .stats-box-warning {
            background: linear-gradient(135deg, var(--secondary) 0%, var(--secondary-dark) 100%);
            color: #333;
        }
        
        .stats-box-info {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
        }
        
        /* Cards */
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        
        /* Tables */
        .table {
            border-radius: 10px;
            overflow: hidden;
        }
        
        .table-scroll-container {
            max-height: 450px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            border-radius: 10px;
        }
        
        .table-scroll-container table {
            margin-bottom: 0;
        }
        
        .table-scroll-container thead {
            position: sticky;
            top: 0;
            z-index: 10;
            background: white;
        }
        
        .table-scroll-container tfoot {
            position: sticky;
            bottom: 0;
            z-index: 10;
            background: white;
        }
        
        .debit { color: var(--primary); font-weight: bold; }
        .kredit { color: #e74c3c; font-weight: bold; }
        .tabungan-badge { background: #3498db !important; }
        
        /* Profile */
        .profile-avatar {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            border: 5px solid var(--primary);
        }
        
        /* Charts */
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        
        .health-score {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        .health-indicator {
            height: 10px;
            border-radius: 5px;
            background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #2ecc71 100%);
            margin: 10px 0;
            position: relative;
        }
        
        .health-pointer {
            width: 20px;
            height: 20px;
            background: white;
            border: 3px solid #333;
            border-radius: 50%;
            position: absolute;
            top: -5px;
            transform: translateX(-50%);
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            :root {
                --sidebar-width: 0px;
            }
            
            .mobile-menu-toggle {
                display: block;
            }
            
            .sidebar {
                transform: translateX(-100%);
                width: 280px;
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .mobile-overlay.active {
                display: block;
            }
            
            .main-content {
                margin-left: 0;
                padding: 80px 15px 15px 15px;
            }
            
            .content-wrapper {
                padding: 20px 15px;
            }
            
            /* Stats boxes responsive */
            .stats-box {
                margin: 10px 0;
            }
            
            .stats-box h6 {
                font-size: 12px;
            }
            
            .stats-box h3 {
                font-size: 18px;
            }
            
            .stats-box small {
                font-size: 11px;
            }
            
            /* Health score responsive */
            .health-score {
                font-size: 36px;
            }
            
            /* Chart responsive */
            .chart-container {
                height: 300px;
            }
            
            /* Table responsive */
            .table-scroll-container {
                max-height: 400px;
                font-size: 14px;
            }
            
            .table th,
            .table td {
                padding: 8px 5px;
                font-size: 13px;
            }
            
            /* Form responsive */
            .form-label {
                font-size: 14px;
            }
            
            .form-control,
            .form-select {
                font-size: 14px;
            }
            
            .btn {
                font-size: 14px;
                padding: 8px 16px;
            }
            
            /* Profile avatar responsive */
            .profile-avatar {
                width: 100px;
                height: 100px;
                border: 3px solid var(--primary);
            }
            
            /* Modal responsive */
            .modal-dialog {
                margin: 10px;
            }
            
            /* Hide some text on mobile */
            .sidebar .brand {
                font-size: 16px;
            }
            
            /* Card title responsive */
            .card-title {
                font-size: 16px;
            }
            
            /* Alert responsive */
            .alert {
                font-size: 14px;
                padding: 10px;
            }
        }
        
        @media (max-width: 480px) {
            .main-content {
                padding: 70px 10px 10px 10px;
            }
            
            .content-wrapper {
                padding: 15px 10px;
                border-radius: 10px;
            }
            
            h3 {
                font-size: 20px;
            }
            
            h5 {
                font-size: 16px;
            }
            
            .stats-box h3 {
                font-size: 16px;
            }
            
            .health-score {
                font-size: 28px;
            }
            
            .chart-container {
                height: 250px;
            }
            
            .table-scroll-container {
                font-size: 12px;
                max-height: 350px;
            }
            
            .table th,
            .table td {
                padding: 6px 4px;
                font-size: 12px;
            }
            
            .profile-avatar {
                width: 80px;
                height: 80px;
            }
        }
    </style>
</head>
<body>
    <!-- Mobile Menu Toggle Button -->
    <button class="mobile-menu-toggle" onclick="toggleMobileMenu()">
        <i class="bi bi-list"></i>
    </button>
    
    <!-- Mobile Overlay -->
    <div class="mobile-overlay" id="mobileOverlay" onclick="toggleMobileMenu()"></div>
    
    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="logo">💰</div>
        <div class="brand">Keuangan Pro</div>
        
        <div class="user-info">
            <img src="{{ user.foto_profil or '/static/default-avatar.png' }}" class="user-avatar" alt="Avatar" onerror="this.src='https://via.placeholder.com/45'">
            <div>
                <div class="user-name">{{ user.nama_lengkap or user.username }}</div>
                <div class="user-email">{{ user.email[:20] }}...</div>
            </div>
        </div>
        
        <a href="#" class="nav-link active" onclick="showTab('dashboard')">
            <i class="bi bi-speedometer2"></i><span> Dashboard</span>
        </a>
        <a href="#" class="nav-link" onclick="showTab('transaksi')">
            <i class="bi bi-plus-circle"></i><span> Transaksi</span>
        </a>
        <a href="#" class="nav-link" onclick="showTab('riwayat')">
            <i class="bi bi-clock-history"></i><span> Riwayat</span>
        </a>
        <a href="#" class="nav-link" onclick="showTab('bukubesar')">
            <i class="bi bi-journal-text"></i><span> Buku Besar</span>
        </a>
        <a href="#" class="nav-link" onclick="showTab('tabungan')">
            <i class="bi bi-piggy-bank"></i><span> Tabungan</span>
        </a>
        <a href="#" class="nav-link" onclick="showTab('profil')">
            <i class="bi bi-person-circle"></i><span> Profil</span>
        </a>
        
        <button class="logout-btn" onclick="location.href='/logout'">
            <i class="bi bi-box-arrow-right"></i> Logout
        </button>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
        <!-- Dashboard Tab -->
        <div id="dashboard" class="content-wrapper">
            <h3><i class="bi bi-speedometer2"></i> Dashboard</h3>
            <hr>
            <div id="summaryStats"></div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">📊 Distribusi Keuangan</h5>
                            <div class="chart-container">
                                <canvas id="pieChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">📈 Tren Keuangan</h5>
                            <div class="chart-container">
                                <canvas id="barChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Transaksi Tab -->
        <div id="transaksi" class="content-wrapper" style="display:none;">
            <h3><i class="bi bi-plus-circle"></i> Tambah Transaksi</h3>
            <hr>
            <form id="transaksiForm">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Tanggal</label>
                            <input type="date" class="form-control" id="tanggal" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Tipe Transaksi</label>
                            <select class="form-select" id="tipe" required onchange="updateKategori()">
                                <option value="Pengeluaran">Pengeluaran</option>
                                <option value="Pemasukan">Pemasukan</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Kategori</label>
                    <select class="form-select" id="kategori" required></select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Jumlah (Rp)</label>
                    <input type="number" class="form-control" id="jumlah" required min="1">
                </div>
                <div class="mb-3">
                    <label class="form-label">Keterangan</label>
                    <textarea class="form-control" id="keterangan" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-save"></i> Simpan Transaksi
                </button>
            </form>
            <div id="transaksiStatus" class="mt-3"></div>
        </div>

        <!-- Riwayat Tab -->
        <div id="riwayat" class="content-wrapper" style="display:none;">
            <h3><i class="bi bi-clock-history"></i> Riwayat Transaksi</h3>
            <hr>
            <div class="table-scroll-container">
                <table class="table table-striped table-hover mb-0" id="riwayatTable">
                    <thead class="table-success">
                        <tr>
                            <th>Tanggal</th>
                            <th>Tipe</th>
                            <th>Kategori</th>
                            <th>Jumlah</th>
                            <th>Keterangan</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <!-- Buku Besar Tab -->
        <div id="bukubesar" class="content-wrapper" style="display:none;">
            <h3><i class="bi bi-journal-text"></i> Buku Besar</h3>
            <hr>
            <div class="row mb-3">
                <div class="col-md-4">
                    <label class="form-label">Filter Kategori</label>
                    <select class="form-select" id="filterKategori" onchange="loadBukuBesar()">
                        <option value="">Semua Kategori</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Dari Tanggal</label>
                    <input type="date" class="form-control" id="filterTanggalMulai" onchange="loadBukuBesar()">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Sampai Tanggal</label>
                    <input type="date" class="form-control" id="filterTanggalAkhir" onchange="loadBukuBesar()">
                </div>
            </div>
            <button class="btn btn-primary mb-3" onclick="loadBukuBesar()">
                <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
            <div class="table-scroll-container">
                <table class="table table-bordered table-hover mb-0" id="bukuBesarTable">
                    <thead class="table-success">
                        <tr>
                            <th>Tanggal</th>
                            <th>Keterangan</th>
                            <th>Kategori</th>
                            <th class="text-end">Debit</th>
                            <th class="text-end">Kredit</th>
                            <th class="text-end">Saldo</th>
                        </tr>
                    </thead>
                    <tbody id="bukuBesarBody"></tbody>
                    <tfoot class="table-warning">
                        <tr id="bukuBesarTotal"></tr>
                    </tfoot>
                </table>
            </div>
        </div>

        <!-- Tabungan Tab -->
        <div id="tabungan" class="content-wrapper" style="display:none;">
            <h3><i class="bi bi-piggy-bank"></i> Kelola Tabungan</h3>
            <hr>
            <div id="tabunganInfo" class="stats-box stats-box-warning mb-3"></div>
            <div id="saldoInfo" class="alert alert-info"></div>
            <form id="tabunganForm">
                <div class="mb-3">
                    <label class="form-label">Aksi</label>
                    <select class="form-select" id="aksiTabungan">
                        <option value="tambah">Tambah ke Tabungan</option>
                        <option value="ambil">Ambil dari Tabungan</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Jumlah (Rp)</label>
                    <input type="number" class="form-control" id="jumlahTabungan" required min="1">
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-check-circle"></i> Proses
                </button>
            </form>
            <div id="tabunganStatus" class="mt-3"></div>
        </div>

        <!-- Profil Tab -->
        <div id="profil" class="content-wrapper" style="display:none;">
            <h3><i class="bi bi-person-circle"></i> Profil Saya</h3>
            <hr>
            
            <div class="text-center mb-4">
                <img src="{{ user.foto_profil or 'https://via.placeholder.com/150' }}" class="profile-avatar mb-3" id="profilePreview" alt="Foto Profil">
                <br>
                <label for="fotoUpload" class="btn btn-primary">
                    <i class="bi bi-camera"></i> Ubah Foto
                </label>
                <input type="file" id="fotoUpload" accept="image/*" style="display:none" onchange="uploadFoto()">
            </div>
            
            <ul class="nav nav-tabs mb-3" id="profilTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="dataProfilTabBtn" data-bs-toggle="tab" data-bs-target="#dataProfilTab" type="button">Data Profil</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="privacyTabBtn" data-bs-toggle="tab" data-bs-target="#privacyTab" type="button">Privacy & Security</button>
                </li>
            </ul>
            
            <div class="tab-content">
                <div class="tab-pane fade show active" id="dataProfilTab">
                    <form id="profilForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control" value="{{ user.username }}" disabled>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" value="{{ user.email }}" disabled>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nama Lengkap</label>
                                    <input type="text" class="form-control" id="namaLengkap" value="{{ user.nama_lengkap or '' }}">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Tanggal Lahir</label>
                                    <input type="date" class="form-control" id="tanggalLahir" value="{{ user.tanggal_lahir or '' }}">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Jenis Kelamin</label>
                                    <select class="form-select" id="jenisKelamin">
                                        <option value="">Pilih</option>
                                        <option value="Laki-laki" {{ 'selected' if user.jenis_kelamin == 'Laki-laki' else '' }}>Laki-laki</option>
                                        <option value="Perempuan" {{ 'selected' if user.jenis_kelamin == 'Perempuan' else '' }}>Perempuan</option>
                                        <option value="Lainnya" {{ 'selected' if user.jenis_kelamin == 'Lainnya' else '' }}>Lainnya</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">No. Telepon</label>
                                    <input type="tel" class="form-control" id="noTelepon" value="{{ user.no_telepon or '' }}">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Alamat</label>
                            <textarea class="form-control" id="alamat" rows="3">{{ user.alamat or '' }}</textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save"></i> Simpan Perubahan
                        </button>
                    </form>
                    <div id="profilStatus" class="mt-3"></div>
                </div>
                
                <div class="tab-pane fade" id="privacyTab">
                    <h5>Reset Password</h5>
                    <form id="passwordForm">
                        <div class="mb-3">
                            <label class="form-label">Password Saat Ini</label>
                            <input type="password" class="form-control" id="currentPassword" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password Baru</label>
                            <input type="password" class="form-control" id="newPassword" required minlength="6">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Konfirmasi Password Baru</label>
                            <input type="password" class="form-control" id="confirmPassword" required minlength="6">
                        </div>
                        <button type="submit" class="btn btn-warning">
                            <i class="bi bi-shield-lock"></i> Reset Password
                        </button>
                    </form>
                    <div id="passwordStatus" class="mt-3"></div>
                    
                    <hr class="my-4">
                    
                    <h5 class="text-danger">⚠️ Zona Berbahaya</h5>
                    <div class="alert alert-danger">
                        <strong>Reset Data</strong><br>
                        Menghapus semua data transaksi, tabungan, dan riwayat keuangan Anda. Data profil tetap tersimpan.<br>
                        <small class="text-muted">⚠️ Tindakan ini tidak dapat dibatalkan!</small>
                    </div>
                    <button type="button" class="btn btn-danger" onclick="showResetDataModal()">
                        <i class="bi bi-trash"></i> Reset Data Keuangan
                    </button>
                    <div id="resetStatus" class="mt-3"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Reset Data -->
    <div class="modal fade" id="resetDataModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title"><i class="bi bi-exclamation-triangle"></i> Konfirmasi Reset Data</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-warning">
                        <strong>⚠️ PERINGATAN!</strong><br>
                        Anda akan menghapus SEMUA data keuangan termasuk:
                        <ul class="mt-2 mb-0">
                            <li>Semua transaksi (Pemasukan & Pengeluaran)</li>
                            <li>Data tabungan</li>
                            <li>Riwayat transaksi</li>
                        </ul>
                    </div>
                    <p class="text-danger"><strong>Tindakan ini TIDAK DAPAT dibatalkan!</strong></p>
                    <p>Masukkan password Anda untuk melanjutkan:</p>
                    <form id="resetDataForm">
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" id="resetPassword" required placeholder="Masukkan password Anda">
                        </div>
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="confirmReset" required>
                            <label class="form-check-label" for="confirmReset">
                                Saya memahami bahwa data tidak dapat dikembalikan
                            </label>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-circle"></i> Batal
                    </button>
                    <button type="button" class="btn btn-danger" onclick="executeResetData()">
                        <i class="bi bi-trash"></i> Ya, Hapus Semua Data
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Mobile Menu Toggle
        function toggleMobileMenu() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('mobileOverlay');
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }
        
        // Close mobile menu when clicking nav link
        document.addEventListener('DOMContentLoaded', function() {
            const navLinks = document.querySelectorAll('.sidebar .nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    if (window.innerWidth <= 768) {
                        toggleMobileMenu();
                    }
                });
            });
        });
        
        // Global chart instances
        let pieChart = null;
        let barChart = null;
        
        // Kategori berdasarkan tipe
        const kategoriPemasukan = ['Gaji', 'Hibah', 'Lainnya'];
        const kategoriPengeluaran = ['Jajan', 'Transportasi', 'Makan', 'Kebutuhan', 'Keinginan', 'Lainnya'];
        
        window.onload = function() {
            initDateLimits();
            updateKategori();
            refreshDashboard();
            loadSummary();
            loadTabunganInfo();
            updateFilterKategori();
            
            const today = new Date();
            const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
            document.getElementById('filterTanggalMulai').value = firstDay.toISOString().split('T')[0];
            document.getElementById('filterTanggalAkhir').value = today.toISOString().split('T')[0];
        };
        
        // Inisialisasi limit tanggal (seminggu ke depan dan ke belakang)
        function initDateLimits() {
            const today = new Date();
            const weekBefore = new Date(today);
            weekBefore.setDate(today.getDate() - 7);
            const weekAfter = new Date(today);
            weekAfter.setDate(today.getDate() + 7);
            
            const tanggalInput = document.getElementById('tanggal');
            tanggalInput.min = weekBefore.toISOString().split('T')[0];
            tanggalInput.max = weekAfter.toISOString().split('T')[0];
            tanggalInput.value = today.toISOString().split('T')[0];
        }
        
        // Update kategori berdasarkan tipe
        function updateKategori() {
            const tipe = document.getElementById('tipe').value;
            const kategoriSelect = document.getElementById('kategori');
            kategoriSelect.innerHTML = '';
            
            const kategoriList = tipe === 'Pemasukan' ? kategoriPemasukan : kategoriPengeluaran;
            kategoriList.forEach(kat => {
                const option = document.createElement('option');
                option.value = kat;
                option.textContent = kat;
                kategoriSelect.appendChild(option);
            });
        }
        
        // Update filter kategori di buku besar
        function updateFilterKategori() {
            const filterSelect = document.getElementById('filterKategori');
            filterSelect.innerHTML = '<option value="">Semua Kategori</option>';
            
            [...kategoriPemasukan, ...kategoriPengeluaran].forEach(kat => {
                const option = document.createElement('option');
                option.value = kat;
                option.textContent = kat;
                filterSelect.appendChild(option);
            });
        }
        
        // Show tab
        function showTab(tabName) {
            document.querySelectorAll('.content-wrapper').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabName).style.display = 'block';
            event.target.closest('.nav-link').classList.add('active');
            
            if (tabName === 'riwayat') loadRiwayat();
            if (tabName === 'bukubesar') loadBukuBesar();
            if (tabName === 'dashboard') refreshDashboard();
        }
        
        function calculateHealthScore(data) {
            let score = 50; // Base score
            
            // Tabungan factor (max +20)
            if (data.tabungan > 0) {
                const tabunganRatio = data.tabungan / (data.pemasukan || 1);
                score += Math.min(20, tabunganRatio * 100);
            }
            
            // Saldo factor (max +15)
            if (data.saldo > 0) {
                const saldoRatio = data.saldo / (data.pemasukan || 1);
                score += Math.min(15, saldoRatio * 50);
            } else {
                score -= 15;
            }
            
            // Arus kas factor (max +10)
            if (data.arus_kas > 0) {
                score += 10;
            } else {
                score -= 10;
            }
            
            // Pengeluaran ratio factor (max +5)
            if (data.pemasukan > 0) {
                const pengeluaranRatio = data.pengeluaran / data.pemasukan;
                if (pengeluaranRatio < 0.5) {
                    score += 5;
                } else if (pengeluaranRatio > 0.9) {
                    score -= 10;
                }
            }
            
            return Math.max(0, Math.min(100, Math.round(score)));
        }
        
        function getHealthStatus(score) {
            if (score >= 80) return { text: 'Sangat Sehat', color: '#2ecc71', emoji: '😄' };
            if (score >= 60) return { text: 'Sehat', color: '#27ae60', emoji: '🙂' };
            if (score >= 40) return { text: 'Cukup', color: '#f39c12', emoji: '😐' };
            if (score >= 20) return { text: 'Perlu Perhatian', color: '#e67e22', emoji: '😟' };
            return { text: 'Buruk', color: '#e74c3c', emoji: '😰' };
        }
        
        function refreshDashboard() {
            loadSummary();
            loadChartData();
        }

        function loadSummary() {
            fetch('/api/summary')
                .then(response => response.json())
                .then(data => {
                    const healthScore = calculateHealthScore(data);
                    const healthStatus = getHealthStatus(healthScore);
                    
                    document.getElementById('summaryStats').innerHTML = `
                        <div class="row">
                            <div class="col-md-3">
                                <div class="stats-box stats-box-info">
                                    <h6>📊 Arus Kas Bersih</h6>
                                    <h3>Rp ${data.arus_kas.toLocaleString('id-ID')}</h3>
                                    <small>${data.arus_kas >= 0 ? '✅ Positif' : '⚠️ Negatif'}</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="stats-box">
                                    <h6>💵 Saldo Tersedia</h6>
                                    <h3>Rp ${data.saldo.toLocaleString('id-ID')}</h3>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="stats-box stats-box-warning">
                                    <h6>💎 Tabungan</h6>
                                    <h3>Rp ${data.tabungan.toLocaleString('id-ID')}</h3>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="stats-box" style="background: linear-gradient(135deg, ${healthStatus.color} 0%, ${healthStatus.color}dd 100%);">
                                    <h6>❤️ Health Score</h6>
                                    <div class="health-score">${healthScore} ${healthStatus.emoji}</div>
                                    <div class="health-indicator">
                                        <div class="health-pointer" style="left: ${healthScore}%;"></div>
                                    </div>
                                    <small style="text-align: center; display: block; margin-top: 10px;">${healthStatus.text}</small>
                                </div>
                            </div>
                        </div>
                    `;
                });
        }
        
        function loadChartData() {
            fetch('/api/chart-data')
                .then(response => response.json())
                .then(data => {
                    // Destroy existing charts
                    if (pieChart) pieChart.destroy();
                    if (barChart) barChart.destroy();
                    
                    // Pie Chart - Distribusi Pengeluaran
                    const pieCtx = document.getElementById('pieChart').getContext('2d');
                    pieChart = new Chart(pieCtx, {
                        type: 'pie',
                        data: {
                            labels: data.kategori_labels,
                            datasets: [{
                                data: data.kategori_values,
                                backgroundColor: [
                                    '#2ecc71', '#27ae60', '#f1c40f', 
                                    '#f39c12', '#e67e22', '#e74c3c'
                                ],
                                borderWidth: 2,
                                borderColor: '#fff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return context.label + ': Rp ' + context.parsed.toLocaleString('id-ID');
                                        }
                                    }
                                }
                            }
                        }
                    });
                    
                    // Bar Chart - Perbandingan
                    const barCtx = document.getElementById('barChart').getContext('2d');
                    barChart = new Chart(barCtx, {
                        type: 'bar',
                        data: {
                            labels: ['Pemasukan', 'Pengeluaran', 'Tabungan', 'Saldo'],
                            datasets: [{
                                label: 'Jumlah (Rp)',
                                data: [data.pemasukan, data.pengeluaran, data.tabungan, data.saldo],
                                backgroundColor: [
                                    '#2ecc71',
                                    '#e74c3c',
                                    '#f1c40f',
                                    data.saldo >= 0 ? '#27ae60' : '#c0392b'
                                ],
                                borderWidth: 2,
                                borderColor: '#fff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return 'Rp ' + context.parsed.y.toLocaleString('id-ID');
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            return 'Rp ' + value.toLocaleString('id-ID');
                                        }
                                    }
                                }
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading chart data:', error));
        }

        document.getElementById('transaksiForm').onsubmit = function(e) {
            e.preventDefault();
            const data = {
                tanggal: document.getElementById('tanggal').value,
                tipe: document.getElementById('tipe').value,
                kategori: document.getElementById('kategori').value,
                jumlah: document.getElementById('jumlah').value,
                keterangan: document.getElementById('keterangan').value
            };

            fetch('/api/transaksi', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.getElementById('transaksiStatus').innerHTML = 
                        `<div class="alert alert-success">${result.message}</div>`;
                    document.getElementById('transaksiForm').reset();
                    initDateLimits();
                    updateKategori();
                    loadSummary();
                } else {
                    document.getElementById('transaksiStatus').innerHTML = 
                        `<div class="alert alert-danger">${result.message}</div>`;
                }
            });
        };

        function loadRiwayat() {
            fetch('/api/riwayat')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.querySelector('#riwayatTable tbody');
                    tbody.innerHTML = '';
                    data.forEach(item => {
                        let badgeClass = 'success';
                        let badgeText = item.tipe;
                        
                        if (item.tipe === 'Tabungan') {
                            badgeClass = 'primary tabungan-badge';
                        } else if (item.tipe === 'Pengeluaran') {
                            badgeClass = 'danger';
                        }
                        
                        tbody.innerHTML += `
                            <tr>
                                <td>${new Date(item.tanggal).toLocaleDateString('id-ID')}</td>
                                <td><span class="badge bg-${badgeClass}">${badgeText}</span></td>
                                <td>${item.kategori}</td>
                                <td class="${item.tipe === 'Pemasukan' ? 'debit' : 'kredit'}">Rp ${parseFloat(item.jumlah).toLocaleString('id-ID')}</td>
                                <td>${item.keterangan || '-'}</td>
                            </tr>
                        `;
                    });
                });
        }

        function loadBukuBesar() {
            const kategori = document.getElementById('filterKategori').value;
            const tanggalMulai = document.getElementById('filterTanggalMulai').value;
            const tanggalAkhir = document.getElementById('filterTanggalAkhir').value;
            
            const params = new URLSearchParams({
                kategori: kategori,
                tanggal_mulai: tanggalMulai,
                tanggal_akhir: tanggalAkhir,
                limit: 10  // Batasi hanya 10 baris terakhir
            });
            
            fetch(`/api/buku-besar?${params}`)
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('bukuBesarBody');
                    tbody.innerHTML = '';
                    
                    let saldo = 0;
                    data.entries.forEach(entry => {
                        saldo += parseFloat(entry.debit) - parseFloat(entry.kredit);
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${new Date(entry.tanggal).toLocaleDateString('id-ID')}</td>
                            <td>${entry.keterangan}</td>
                            <td>${entry.kategori}</td>
                            <td class="text-end debit">${entry.debit > 0 ? 'Rp ' + parseFloat(entry.debit).toLocaleString('id-ID') : '-'}</td>
                            <td class="text-end kredit">${entry.kredit > 0 ? 'Rp ' + parseFloat(entry.kredit).toLocaleString('id-ID') : '-'}</td>
                            <td class="text-end"><strong>Rp ${saldo.toLocaleString('id-ID')}</strong></td>
                        `;
                        tbody.appendChild(row);
                    });
                    
                    document.getElementById('bukuBesarTotal').innerHTML = `
                        <td colspan="3" class="text-end"><strong>TOTAL:</strong></td>
                        <td class="text-end debit"><strong>Rp ${data.total_debit.toLocaleString('id-ID')}</strong></td>
                        <td class="text-end kredit"><strong>Rp ${data.total_kredit.toLocaleString('id-ID')}</strong></td>
                        <td class="text-end"><strong>Rp ${data.saldo_akhir.toLocaleString('id-ID')}</strong></td>
                    `;
                });
        }

        function loadTabunganInfo() {
            Promise.all([
                fetch('/api/tabungan').then(r => r.json()),
                fetch('/api/summary').then(r => r.json())
            ]).then(([tabunganData, summaryData]) => {
                document.getElementById('tabunganInfo').innerHTML = `
                    <h3>💎 Saldo Tabungan</h3>
                    <h2>Rp ${tabunganData.jumlah.toLocaleString('id-ID')}</h2>
                `;
                
                document.getElementById('saldoInfo').innerHTML = `
                    <strong>💵 Saldo Tersedia untuk Ditabung:</strong> Rp ${summaryData.saldo.toLocaleString('id-ID')}
                    <br><small class="text-muted">Saldo ini adalah hasil dari: Pemasukan - Pengeluaran (termasuk yang sudah masuk tabungan)</small>
                `;
            });
        }

        document.getElementById('tabunganForm').onsubmit = function(e) {
            e.preventDefault();
            const data = {
                aksi: document.getElementById('aksiTabungan').value,
                jumlah: document.getElementById('jumlahTabungan').value
            };

            fetch('/api/tabungan/kelola', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('tabunganStatus').innerHTML = 
                    `<div class="alert alert-${result.success ? 'success' : 'danger'}">${result.message}</div>`;
                if (result.success) {
                    document.getElementById('tabunganForm').reset();
                    loadTabunganInfo();
                    loadSummary();
                    loadRiwayat();
                }
            });
        };

        document.getElementById('profilForm').onsubmit = function(e) {
            e.preventDefault();
            const data = {
                nama_lengkap: document.getElementById('namaLengkap').value,
                tanggal_lahir: document.getElementById('tanggalLahir').value,
                jenis_kelamin: document.getElementById('jenisKelamin').value,
                no_telepon: document.getElementById('noTelepon').value,
                alamat: document.getElementById('alamat').value
            };

            fetch('/api/profil/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('profilStatus').innerHTML = 
                    `<div class="alert alert-${result.success ? 'success' : 'danger'}">${result.message}</div>`;
                if (result.success) {
                    setTimeout(() => location.reload(), 1500);
                }
            });
        };

        document.getElementById('passwordForm').onsubmit = function(e) {
            e.preventDefault();
            const newPass = document.getElementById('newPassword').value;
            const confirmPass = document.getElementById('confirmPassword').value;
            
            if (newPass !== confirmPass) {
                document.getElementById('passwordStatus').innerHTML = 
                    '<div class="alert alert-danger">Password baru tidak cocok!</div>';
                return;
            }
            
            const data = {
                current_password: document.getElementById('currentPassword').value,
                new_password: newPass
            };

            fetch('/api/profil/reset-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('passwordStatus').innerHTML = 
                    `<div class="alert alert-${result.success ? 'success' : 'danger'}">${result.message}</div>`;
                if (result.success) {
                    document.getElementById('passwordForm').reset();
                    setTimeout(() => location.href = '/logout', 2000);
                }
            });
        };

        function uploadFoto() {
            const fileInput = document.getElementById('fotoUpload');
            const file = fileInput.files[0];
            
            if (!file) return;
            
            const formData = new FormData();
            formData.append('foto', file);
            
            fetch('/api/profil/upload-foto', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.getElementById('profilePreview').src = result.foto_url + '?t=' + new Date().getTime();
                    document.getElementById('profilStatus').innerHTML = 
                        `<div class="alert alert-success">${result.message}</div>`;
                    setTimeout(() => location.reload(), 1500);
                } else {
                    document.getElementById('profilStatus').innerHTML = 
                        `<div class="alert alert-danger">${result.message}</div>`;
                }
            });
        }
        
        // Reset Data Functions
        let resetDataModal;
        
        function showResetDataModal() {
            if (!resetDataModal) {
                resetDataModal = new bootstrap.Modal(document.getElementById('resetDataModal'));
            }
            document.getElementById('resetDataForm').reset();
            resetDataModal.show();
        }
        
        function executeResetData() {
            const password = document.getElementById('resetPassword').value;
            const confirmed = document.getElementById('confirmReset').checked;
            
            if (!password) {
                alert('Mohon masukkan password Anda!');
                return;
            }
            
            if (!confirmed) {
                alert('Mohon centang konfirmasi untuk melanjutkan!');
                return;
            }
            
            // Kirim request reset data
            fetch('/api/profil/reset-data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ password: password })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    resetDataModal.hide();
                    document.getElementById('resetStatus').innerHTML = 
                        `<div class="alert alert-success">${result.message}</div>`;
                    
                    // Reload setelah 2 detik
                    setTimeout(() => {
                        location.href = '/';
                    }, 2000);
                } else {
                    document.getElementById('resetStatus').innerHTML = 
                        `<div class="alert alert-danger">${result.message}</div>`;
                    resetDataModal.hide();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('resetStatus').innerHTML = 
                    `<div class="alert alert-danger">Terjadi kesalahan saat reset data!</div>`;
                resetDataModal.hide();
            });
        }
    </script>
</body>
</html>
"""

# Routes untuk Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('index'))
            else:
                return render_template_string(LOGIN_TEMPLATE, 
                    title='Login', 
                    is_register=False, 
                    error='Username/Email atau password salah!')
        except Exception as e:
            return render_template_string(LOGIN_TEMPLATE, 
                title='Login', 
                is_register=False, 
                error=f'Error: {str(e)}')
    
    return render_template_string(LOGIN_TEMPLATE, title='Login', is_register=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template_string(LOGIN_TEMPLATE, 
                title='Register', 
                is_register=True, 
                error='Password tidak cocok!')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template_string(LOGIN_TEMPLATE, 
                    title='Register', 
                    is_register=True, 
                    error='Username sudah digunakan!')
            
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template_string(LOGIN_TEMPLATE, 
                    title='Register', 
                    is_register=True, 
                    error='Email sudah digunakan!')
            
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password) 
                VALUES (%s, %s, %s)
            """, (username, email, hashed_password))
            
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO tabungan (user_id, jumlah) VALUES (%s, 0)", (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return render_template_string(LOGIN_TEMPLATE, 
                title='Register', 
                is_register=True, 
                success='Registrasi berhasil! Silakan login.')
        except Exception as e:
            return render_template_string(LOGIN_TEMPLATE, 
                title='Register', 
                is_register=True, 
                error=f'Error: {str(e)}')
    
    return render_template_string(LOGIN_TEMPLATE, title='Register', is_register=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template_string(MAIN_TEMPLATE, user=user)

# API Routes
@app.route('/api/transaksi', methods=['POST'])
@login_required
def tambah_transaksi():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transaksi (user_id, tanggal, tipe, kategori, jumlah, keterangan)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], data['tanggal'], data['tipe'], data['kategori'], data['jumlah'], data['keterangan']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': f'✅ {data["tipe"]} berhasil ditambahkan!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/riwayat', methods=['GET'])
@login_required
def get_riwayat():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transaksi WHERE user_id = %s ORDER BY tanggal DESC, created_at DESC", (session['user_id'],))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/summary', methods=['GET'])
@login_required
def get_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(jumlah) as total FROM transaksi WHERE user_id = %s AND tipe='Pemasukan'", (session['user_id'],))
        pemasukan = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT SUM(jumlah) as total FROM transaksi WHERE user_id = %s AND tipe IN ('Pengeluaran', 'Tabungan')", (session['user_id'],))
        pengeluaran = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT jumlah FROM tabungan WHERE user_id = %s", (session['user_id'],))
        tabungan_row = cursor.fetchone()
        tabungan = tabungan_row['jumlah'] if tabungan_row else 0
        
        cursor.close()
        conn.close()
        
        saldo = float(pemasukan) - float(pengeluaran)
        arus_kas = float(pemasukan) - float(pengeluaran)
        
        return jsonify({
            'pemasukan': float(pemasukan),
            'pengeluaran': float(pengeluaran),
            'saldo': saldo,
            'tabungan': float(tabungan),
            'arus_kas': arus_kas
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/chart-data', methods=['GET'])
@login_required
def get_chart_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Data untuk pie chart - pengeluaran per kategori
        cursor.execute("""
            SELECT kategori, SUM(jumlah) as total 
            FROM transaksi 
            WHERE user_id = %s AND tipe = 'Pengeluaran'
            GROUP BY kategori
        """, (session['user_id'],))
        kategori_data = cursor.fetchall()
        
        kategori_labels = [item['kategori'] for item in kategori_data]
        kategori_values = [float(item['total']) for item in kategori_data]
        
        # Data untuk bar chart
        cursor.execute("SELECT SUM(jumlah) as total FROM transaksi WHERE user_id = %s AND tipe='Pemasukan'", (session['user_id'],))
        pemasukan = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT SUM(jumlah) as total FROM transaksi WHERE user_id = %s AND tipe IN ('Pengeluaran', 'Tabungan')", (session['user_id'],))
        pengeluaran = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT jumlah FROM tabungan WHERE user_id = %s", (session['user_id'],))
        tabungan_row = cursor.fetchone()
        tabungan = tabungan_row['jumlah'] if tabungan_row else 0
        
        cursor.close()
        conn.close()
        
        saldo = float(pemasukan) - float(pengeluaran)
        
        return jsonify({
            'kategori_labels': kategori_labels,
            'kategori_values': kategori_values,
            'pemasukan': float(pemasukan),
            'pengeluaran': float(pengeluaran),
            'tabungan': float(tabungan),
            'saldo': saldo
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/buku-besar', methods=['GET'])
@login_required
def get_buku_besar():
    try:
        kategori = request.args.get('kategori', '')
        tanggal_mulai = request.args.get('tanggal_mulai', '')
        tanggal_akhir = request.args.get('tanggal_akhir', '')
        limit = request.args.get('limit', None)  # Ambil parameter limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM transaksi WHERE user_id = %s"
        params = [session['user_id']]
        
        if kategori:
            query += " AND kategori = %s"
            params.append(kategori)
        
        if tanggal_mulai:
            query += " AND DATE(tanggal) >= %s"
            params.append(tanggal_mulai)
        
        if tanggal_akhir:
            query += " AND DATE(tanggal) <= %s"
            params.append(tanggal_akhir)
        
        query += " ORDER BY tanggal DESC, created_at DESC"
        
        # Tambahkan LIMIT jika ada
        if limit:
            query += f" LIMIT {int(limit)}"
        
        cursor.execute(query, params)
        transaksi = cursor.fetchall()
        
        # Reverse untuk menampilkan yang terlama dulu, tapi tetap ambil 10 terakhir
        transaksi.reverse()
        
        entries = []
        total_debit = 0
        total_kredit = 0
        
        for t in transaksi:
            if t['tipe'] == 'Pemasukan':
                debit = float(t['jumlah'])
                kredit = 0
                total_debit += debit
            else:  # Pengeluaran atau Tabungan
                debit = 0
                kredit = float(t['jumlah'])
                total_kredit += kredit
            
            entries.append({
                'tanggal': t['tanggal'],
                'keterangan': t['keterangan'] or '-',
                'kategori': t['kategori'],
                'debit': debit,
                'kredit': kredit
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'entries': entries,
            'total_debit': total_debit,
            'total_kredit': total_kredit,
            'saldo_akhir': total_debit - total_kredit
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/tabungan', methods=['GET'])
@login_required
def get_tabungan():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT jumlah FROM tabungan WHERE user_id = %s", (session['user_id'],))
        result = cursor.fetchone()
        
        if not result:
            cursor.execute("INSERT INTO tabungan (user_id, jumlah) VALUES (%s, 0)", (session['user_id'],))
            conn.commit()
            result = {'jumlah': 0}
        
        cursor.close()
        conn.close()
        return jsonify({'jumlah': float(result['jumlah'])})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/tabungan/kelola', methods=['POST'])
@login_required
def kelola_tabungan():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ambil saldo tersedia (tidak termasuk tabungan)
        cursor.execute("SELECT SUM(jumlah) as total FROM transaksi WHERE user_id = %s AND tipe='Pemasukan'", (session['user_id'],))
        pemasukan = cursor.fetchone()['total'] or 0
        
        cursor.execute("SELECT SUM(jumlah) as total FROM transaksi WHERE user_id = %s AND tipe IN ('Pengeluaran', 'Tabungan')", (session['user_id'],))
        pengeluaran = cursor.fetchone()['total'] or 0
        
        saldo_tersedia = float(pemasukan) - float(pengeluaran)
        
        cursor.execute("SELECT jumlah FROM tabungan WHERE user_id = %s", (session['user_id'],))
        result = cursor.fetchone()
        
        if not result:
            cursor.execute("INSERT INTO tabungan (user_id, jumlah) VALUES (%s, 0)", (session['user_id'],))
            conn.commit()
            current_tabungan = 0
        else:
            current_tabungan = float(result['jumlah'])
        
        if data['aksi'] == 'tambah':
            # Cek apakah saldo tersedia cukup
            if float(data['jumlah']) > saldo_tersedia:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': f'❌ Saldo tersedia tidak cukup! Anda hanya punya Rp {saldo_tersedia:,.0f}'})
            
            # Tambah ke tabungan
            new_tabungan = current_tabungan + float(data['jumlah'])
            cursor.execute("UPDATE tabungan SET jumlah=%s WHERE user_id=%s", (new_tabungan, session['user_id']))
            
            # Catat sebagai transaksi Tabungan (kredit)
            cursor.execute("""
                INSERT INTO transaksi (user_id, tanggal, tipe, kategori, jumlah, keterangan)
                VALUES (%s, CURDATE(), 'Tabungan', 'Tabungan', %s, 'Menabung')
            """, (session['user_id'], data['jumlah']))
            
            msg = f"✅ Berhasil menambah Rp {float(data['jumlah']):,.0f} ke tabungan!"
        else:
            # Ambil dari tabungan
            if float(data['jumlah']) > current_tabungan:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': '❌ Saldo tabungan tidak cukup!'})
            
            new_tabungan = current_tabungan - float(data['jumlah'])
            cursor.execute("UPDATE tabungan SET jumlah=%s WHERE user_id=%s", (new_tabungan, session['user_id']))
            
            # Catat sebagai transaksi Pemasukan (debit) - karena uang kembali ke saldo
            cursor.execute("""
                INSERT INTO transaksi (user_id, tanggal, tipe, kategori, jumlah, keterangan)
                VALUES (%s, CURDATE(), 'Pemasukan', 'Tabungan', %s, 'Ambil dari tabungan')
            """, (session['user_id'], data['jumlah']))
            
            msg = f"✅ Berhasil mengambil Rp {float(data['jumlah']):,.0f} dari tabungan!"
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/profil/update', methods=['POST'])
@login_required
def update_profil():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET nama_lengkap = %s, tanggal_lahir = %s, jenis_kelamin = %s, 
                no_telepon = %s, alamat = %s
            WHERE id = %s
        """, (
            data.get('nama_lengkap'),
            data.get('tanggal_lahir') or None,
            data.get('jenis_kelamin') or None,
            data.get('no_telepon'),
            data.get('alamat'),
            session['user_id']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': '✅ Profil berhasil diperbarui!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/profil/reset-password', methods=['POST'])
@login_required
def reset_password():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifikasi password saat ini
        cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not check_password_hash(user['password'], data['current_password']):
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '❌ Password saat ini salah!'})
        
        # Update password baru
        new_password_hash = generate_password_hash(data['new_password'])
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password_hash, session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': '✅ Password berhasil diubah! Silakan login kembali.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/api/profil/upload-foto', methods=['POST'])
@login_required
def upload_foto():
    try:
        if 'foto' not in request.files:
            return jsonify({'success': False, 'message': 'Tidak ada file yang diupload'})
        
        file = request.files['foto']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih'})
        
        if file and allowed_file(file.filename):
            filename = f"user_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(filepath)
            
            foto_url = f"/static/uploads/{filename}"
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET foto_profil = %s WHERE id = %s", (foto_url, session['user_id']))
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': '✅ Foto profil berhasil diupload!', 'foto_url': foto_url})
        else:
            return jsonify({'success': False, 'message': 'Format file tidak didukung. Gunakan PNG, JPG, atau JPEG'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    from flask import send_file
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/api/profil/reset-data', methods=['POST'])
@login_required
def reset_data():
    try:
        data = request.json
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'message': '❌ Password tidak boleh kosong!'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifikasi password
        cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '❌ Password salah!'})
        
        # Hapus semua transaksi user
        cursor.execute("DELETE FROM transaksi WHERE user_id = %s", (session['user_id'],))
        
        # Reset tabungan ke 0
        cursor.execute("UPDATE tabungan SET jumlah = 0 WHERE user_id = %s", (session['user_id'],))
        
        # Jika belum ada record tabungan, buat baru
        cursor.execute("SELECT * FROM tabungan WHERE user_id = %s", (session['user_id'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO tabungan (user_id, jumlah) VALUES (%s, 0)", (session['user_id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': '✅ Semua data keuangan berhasil dihapus! Halaman akan dimuat ulang...'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {str(e)}'})

if __name__ == '__main__':
    print("🚀 Memulai aplikasi...")
    print("📦 Menginisialisasi database...")
    
    if init_db():
        print("✅ Database siap!")
        print("🌐 Aplikasi berjalan di:")
        print("   - Local: http://localhost:5000")
        print("   - Network: http://0.0.0.0:5000")
        print("⚠️  Pastikan XAMPP MySQL sudah berjalan!")
        print("\n✨ FITUR VERSI 4.1:")
        print("   ✅ Logika Tabungan Fixed: Diambil dari saldo, tercatat di buku besar")
        print("   ✅ Riwayat menampilkan transaksi tabungan dengan badge biru")
        print("   ✅ Dashboard dengan Arus Kas Bersih & Health Score")
        print("   ✅ Chart interaktif (Chart.js) - Pie & Bar Chart")
        print("   ✅ Auto-refresh Buku Besar saat filter berubah")
        print("   ✅ Bug Privacy & Security tab fixed")
        print("   ✅ Export Excel/CSV dihapus")
        print("   ✅ Reset Data dengan konfirmasi password")
        print("\n💡 Login pertama kali: Daftar akun baru di /register")
        print("\n📱 Akses dari HP:")
        print("   1. Pastikan HP dan komputer di WiFi yang sama")
        print("   2. Cari IP komputer: ipconfig (Windows) atau ifconfig (Mac/Linux)")
        print("   3. Akses dari HP: http://[IP_KOMPUTER]:5000")
        print("   Contoh: http://192.168.1.10:5000\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Gagal menginisialisasi database!")
        print("💡 Pastikan XAMPP MySQL sudah aktif!")