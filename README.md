# 💰 Aplikasi Keuangan Pro - MVC Architecture

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

Muhammad Rabbani Syawal - [GitHub](https://github.com/rabbanisyawal7)

## 🤝 Contributing

Contributions welcome! Please open an issue first.

## 📧 Contact

For questions: rabbanisyawal7@gmail.com

