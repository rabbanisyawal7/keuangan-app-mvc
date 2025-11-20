"""
AUTHENTICATION CONTROLLER
"""
from flask import session
from models.user import User

class AuthController:
    """Controller untuk authentication"""
    
    @staticmethod
    def login(username_or_email, password):
        """
        Login user
        Args:
            username_or_email: username atau email
            password: password
        Returns: tuple (success: Boolean, message: str, user_id: int)
        """
        # Cari user
        user = User.get_by_username_or_email(username_or_email)
        
        if not user:
            return False, "Username/Email tidak ditemukan!", None
        
        # Verifikasi password
        if not User.verify_password(user, password):
            return False, "Password salah!", None
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return True, "Login berhasil!", user['id']
    
    @staticmethod
    def register(username, email, password, confirm_password):
        """
        Register user baru
        Args:
            username: username
            email: email
            password: password
            confirm_password: konfirmasi password
        Returns: tuple (success: Boolean, message: str)
        """
        # Validasi password
        if password != confirm_password:
            return False, "Password tidak cocok!"
        
        if len(password) < 6:
            return False, "Password minimal 6 karakter!"
        
        # Cek username sudah ada
        if User.check_username_exists(username):
            return False, "Username sudah digunakan!"
        
        # Cek email sudah ada
        if User.check_email_exists(email):
            return False, "Email sudah digunakan!"
        
        # Buat user
        user_id = User.create(username, email, password)
        
        if user_id:
            return True, "Registrasi berhasil! Silakan login."
        else:
            return False, "Gagal membuat akun. Coba lagi."
    
    @staticmethod
    def logout():
        """
        Logout user
        """
        session.clear()
    
    @staticmethod
    def get_current_user():
        """
        Dapatkan data user yang sedang login
        Returns: dict user data atau None
        """
        user_id = session.get('user_id')
        if user_id:
            return User.get_by_id(user_id)
        return None
