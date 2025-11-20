"""
PROFIL CONTROLLER
"""
from models.user import User
from models.transaksi import Transaksi
from models.tabungan import Tabungan

class ProfilController:
    """Controller untuk profil user"""
    
    @staticmethod
    def update_profil(user_id, data):
        """
        Update profil user
        Args:
            user_id: ID user
            data: dict data profil
        Returns: tuple (success: Boolean, message: str)
        """
        success = User.update_profile(user_id, data)
        
        if success:
            return True, "✅ Profil berhasil diperbarui!"
        else:
            return False, "❌ Gagal memperbarui profil"
    
    @staticmethod
    def update_password(user_id, current_password, new_password, confirm_password):
        """
        Update password user
        Args:
            user_id: ID user
            current_password: password saat ini
            new_password: password baru
            confirm_password: konfirmasi password baru
        Returns: tuple (success: Boolean, message: str)
        """
        # Validasi
        if new_password != confirm_password:
            return False, "❌ Password baru tidak cocok!"
        
        if len(new_password) < 6:
            return False, "❌ Password minimal 6 karakter!"
        
        # Update password
        return User.update_password(user_id, current_password, new_password)
    
    @staticmethod
    def update_foto(user_id, photo_url):
        """
        Update foto profil
        Args:
            user_id: ID user
            photo_url: URL foto
        Returns: tuple (success: Boolean, message: str)
        """
        success = User.update_photo(user_id, photo_url)
        
        if success:
            return True, "✅ Foto profil berhasil diupload!"
        else:
            return False, "❌ Gagal mengupload foto"
    
    @staticmethod
    def reset_data(user_id, password):
        """
        Reset semua data keuangan user
        Args:
            user_id: ID user
            password: password untuk konfirmasi
        Returns: tuple (success: Boolean, message: str)
        """
        # Verifikasi password
        user = User.get_by_id(user_id)
        if not User.verify_password(user, password):
            return False, "❌ Password salah!"
        
        # Hapus semua transaksi
        Transaksi.delete_all_by_user(user_id)
        
        # Reset tabungan
        Tabungan.reset(user_id)
        
        return True, "✅ Semua data keuangan berhasil dihapus!"