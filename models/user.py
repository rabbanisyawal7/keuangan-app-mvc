"""
USER MODEL
"""
from models.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """Model untuk user/pengguna"""
    
    @staticmethod
    def create(username, email, password):
        """
        Buat user baru
        Args:
            username: username
            email: email
            password: password (plain text, akan di-hash)
        Returns: user_id atau None jika gagal
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (username, email, password) 
                VALUES (%s, %s, %s)
            """, (username, email, hashed_password))
            
            user_id = cursor.lastrowid
            
            # Buat record tabungan untuk user baru
            cursor.execute("""
                INSERT INTO tabungan (user_id, jumlah) 
                VALUES (%s, 0)
            """, (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return user_id
            
        except Exception as e:
            print(f"Error create user: {e}")
            return None
    
    @staticmethod
    def get_by_id(user_id):
        """
        Dapatkan user berdasarkan ID
        Args:
            user_id: ID user
        Returns: dict user data atau None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return user
            
        except Exception as e:
            print(f"Error get user: {e}")
            return None
    
    @staticmethod
    def get_by_username_or_email(username_or_email):
        """
        Dapatkan user berdasarkan username atau email
        Args:
            username_or_email: username atau email
        Returns: dict user data atau None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users 
                WHERE username = %s OR email = %s
            """, (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return user
            
        except Exception as e:
            print(f"Error get user: {e}")
            return None
    
    @staticmethod
    def verify_password(user, password):
        """
        Verifikasi password user
        Args:
            user: dict user data
            password: password plain text
        Returns: Boolean
        """
        if not user:
            return False
        return check_password_hash(user['password'], password)
    
    @staticmethod
    def update_profile(user_id, data):
        """
        Update profil user
        Args:
            user_id: ID user
            data: dict data yang akan diupdate
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET nama_lengkap = %s, 
                    tanggal_lahir = %s, 
                    jenis_kelamin = %s,
                    no_telepon = %s, 
                    alamat = %s
                WHERE id = %s
            """, (
                data.get('nama_lengkap'),
                data.get('tanggal_lahir') or None,
                data.get('jenis_kelamin') or None,
                data.get('no_telepon'),
                data.get('alamat'),
                user_id
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error update profile: {e}")
            return False
    
    @staticmethod
    def update_password(user_id, current_password, new_password):
        """
        Update password user
        Args:
            user_id: ID user
            current_password: password saat ini
            new_password: password baru
        Returns: tuple (success: Boolean, message: str)
        """
        try:
            # Verifikasi password saat ini
            user = User.get_by_id(user_id)
            if not user or not User.verify_password(user, current_password):
                return False, "Password saat ini salah!"
            
            # Update password
            conn = get_db_connection()
            cursor = conn.cursor()
            
            new_password_hash = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE users SET password = %s WHERE id = %s
            """, (new_password_hash, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, "Password berhasil diubah!"
            
        except Exception as e:
            print(f"Error update password: {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def update_photo(user_id, photo_url):
        """
        Update foto profil user
        Args:
            user_id: ID user
            photo_url: URL foto
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET foto_profil = %s WHERE id = %s
            """, (photo_url, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error update photo: {e}")
            return False
    
    @staticmethod
    def check_username_exists(username):
        """
        Cek apakah username sudah digunakan
        Args:
            username: username
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            exists = cursor.fetchone() is not None
            
            cursor.close()
            conn.close()
            
            return exists
            
        except Exception as e:
            print(f"Error check username: {e}")
            return False
    
    @staticmethod
    def check_email_exists(email):
        """
        Cek apakah email sudah digunakan
        Args:
            email: email
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            exists = cursor.fetchone() is not None
            
            cursor.close()
            conn.close()
            
            return exists
            
        except Exception as e:
            print(f"Error check email: {e}")
            return False