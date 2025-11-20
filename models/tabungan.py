"""
TABUNGAN MODEL
"""
from models.database import get_db_connection

class Tabungan:
    """Model untuk tabungan user"""
    
    @staticmethod
    def get_by_user(user_id):
        """
        Dapatkan saldo tabungan user
        Args:
            user_id: ID user
        Returns: float jumlah tabungan
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT jumlah FROM tabungan WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                return float(result['jumlah'])
            else:
                # Buat record tabungan jika belum ada
                Tabungan.create(user_id)
                return 0.0
            
        except Exception as e:
            print(f"Error get tabungan: {e}")
            return 0.0
    
    @staticmethod
    def create(user_id, jumlah=0):
        """
        Buat record tabungan untuk user baru
        Args:
            user_id: ID user
            jumlah: jumlah awal (default 0)
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tabungan (user_id, jumlah) 
                VALUES (%s, %s)
            """, (user_id, jumlah))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error create tabungan: {e}")
            return False
    
    @staticmethod
    def update(user_id, jumlah):
        """
        Update jumlah tabungan
        Args:
            user_id: ID user
            jumlah: jumlah baru
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tabungan SET jumlah = %s WHERE user_id = %s
            """, (jumlah, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error update tabungan: {e}")
            return False
    
    @staticmethod
    def tambah(user_id, jumlah):
        """
        Tambah ke tabungan
        Args:
            user_id: ID user
            jumlah: jumlah yang ditambahkan
        Returns: Boolean
        """
        current = Tabungan.get_by_user(user_id)
        new_amount = current + float(jumlah)
        return Tabungan.update(user_id, new_amount)
    
    @staticmethod
    def kurang(user_id, jumlah):
        """
        Kurangi dari tabungan
        Args:
            user_id: ID user
            jumlah: jumlah yang dikurangi
        Returns: tuple (success: Boolean, message: str)
        """
        current = Tabungan.get_by_user(user_id)
        
        if float(jumlah) > current:
            return False, "Saldo tabungan tidak cukup!"
        
        new_amount = current - float(jumlah)
        success = Tabungan.update(user_id, new_amount)
        
        if success:
            return True, "Berhasil mengambil dari tabungan"
        else:
            return False, "Gagal mengambil dari tabungan"
    
    @staticmethod
    def reset(user_id):
        """
        Reset tabungan ke 0
        Args:
            user_id: ID user
        Returns: Boolean
        """
        return Tabungan.update(user_id, 0)
