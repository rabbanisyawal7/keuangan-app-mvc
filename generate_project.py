"""
AUTO GENERATOR - KEUANGAN APP MVC
=================================
Script ini akan membuat semua file dan folder yang dibutuhkan

CARA PAKAI:
1. Save script ini sebagai generate_project.py
2. Letakkan di folder keuangan-app-mvc (hasil clone GitHub)
3. Jalankan: python generate_project.py
4. Semua file akan ter-generate otomatis!
"""

import os
import sys

def create_directory_structure():
    """Buat struktur folder"""
    folders = [
        'models',
        'controllers',
        'routes',
        'templates',
        'static/css',
        'static/js',
        'static/uploads',
        'utils'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Folder created: {folder}/")
    
    # Buat __init__.py
    init_files = [
        'models/__init__.py',
        'controllers/__init__.py',
        'routes/__init__.py',
        'utils/__init__.py'
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write('# Package initialization\n')
        print(f"✅ File created: {init_file}")

def create_config():
    """Buat config.py"""
    content = '''"""
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
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ File created: config.py")

def create_requirements():
    """Buat requirements.txt"""
    content = '''flask==3.0.0
flask-cors==4.0.0
pymysql==1.1.0
werkzeug==3.0.1
pillow==10.1.0
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(content)
    print("✅ File created: requirements.txt")

def create_gitignore():
    """Buat .gitignore"""
    content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite

# Uploads
static/uploads/*
!static/uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Env
.env
'''
    
    with open('.gitignore', 'w') as f:
        f.write(content)
    print("✅ File created: .gitignore")

def create_readme():
    """Buat README.md"""
    content = '''# 💰 Aplikasi Keuangan Pro - MVC Architecture

Aplikasi pencatat keuangan pribadi dengan Flask menggunakan arsitektur MVC (Model-View-Controller).

## ✨ Fitur

- 📊 Dashboard interaktif dengan Chart.js
- 💵 Manajemen transaksi (Pemasukan & Pengeluaran)
- 💎 Sistem tabungan
- 📖 Buku besar dengan filter
- 👤 Multi-user support
- 🔐 Authentication & Authorization
- 📱 Mobile responsive
- 🎨 Modern UI/UX

## 🚀 Installation

### Prerequisites
- Python 3.8+
- MySQL (XAMPP recommended)
- Git

### Setup

1. **Clone repository**
```bash
git clone https://github.com/YOUR_USERNAME/keuangan-app-mvc.git
cd keuangan-app-mvc
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup database**
- Jalankan XAMPP
- Start MySQL
- Database akan dibuat otomatis saat run app

4. **Run application**
```bash
python app.py
```

5. **Access aplikasi**
- Local: http://localhost:5000
- Network: http://0.0.0.0:5000

## 📁 Project Structure

```
keuangan-app-mvc/
├── app.py                 # Entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
│
├── models/               # Data models
│   ├── database.py
│   ├── user.py
│   ├── transaksi.py
│   └── tabungan.py
│
├── controllers/          # Business logic
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── transaksi_controller.py
│   └── profil_controller.py
│
├── routes/              # URL routes
│   ├── auth_routes.py
│   └── api_routes.py
│
├── templates/           # HTML templates
│   ├── login.html
│   └── main.html
│
├── static/             # Static files
│   ├── css/
│   ├── js/
│   └── uploads/
│
└── utils/              # Helper functions
    └── decorators.py
```

## 🎯 Usage

1. **Register** - Buat akun baru
2. **Login** - Masuk dengan akun Anda
3. **Dashboard** - Lihat summary keuangan
4. **Transaksi** - Tambah pemasukan/pengeluaran
5. **Tabungan** - Kelola tabungan Anda
6. **Buku Besar** - Lihat laporan detail
7. **Profil** - Update data profil

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** MySQL
- **Frontend:** Bootstrap 5, Chart.js
- **Architecture:** MVC Pattern

## 📝 License

MIT License

## 👨‍💻 Author

Your Name - [GitHub](https://github.com/YOUR_USERNAME)

## 🤝 Contributing

Contributions welcome! Please open an issue first.

## 📧 Contact

For questions: your.email@example.com
'''
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ File created: README.md")

def create_env_example():
    """Buat .env.example"""
    content = '''# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=keuangan_db

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
'''
    
    with open('.env.example', 'w') as f:
        f.write(content)
    print("✅ File created: .env.example")

def create_placeholder_gitkeep():
    """Buat .gitkeep untuk folder uploads"""
    with open('static/uploads/.gitkeep', 'w') as f:
        f.write('')
    print("✅ File created: static/uploads/.gitkeep")

def main():
    """Main function"""
    print("=" * 70)
    print("🚀 KEUANGAN APP MVC - PROJECT GENERATOR")
    print("=" * 70)
    print("\nGenerating project structure...\n")
    
    try:
        # Create structure
        create_directory_structure()
        print()
        
        # Create config files
        create_config()
        create_requirements()
        create_gitignore()
        create_readme()
        create_env_example()
        create_placeholder_gitkeep()
        
        print("\n" + "=" * 70)
        print("✅ PROJECT STRUCTURE GENERATED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📋 Next steps:")
        print("1. Copy file models, controllers, routes dari template artifact")
        print("2. Copy templates/login.html dan templates/main.html")
        print("3. Copy app.py (entry point)")
        print("4. Run: python app.py")
        print("\n💡 Atau gunakan template lengkap dari artifact sebelumnya")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
