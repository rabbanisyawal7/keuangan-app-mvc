"""
TRANSAKSI MODEL
"""
from models.database import get_db_connection

class Transaksi:
    """Model untuk transaksi keuangan"""
    
    @staticmethod
    def create(user_id, tanggal, tipe, kategori, jumlah, keterangan=''):
        """
        Buat transaksi baru
        Args:
            user_id: ID user
            tanggal: tanggal transaksi
            tipe: Pemasukan/Pengeluaran/Tabungan
            kategori: kategori transaksi
            jumlah: jumlah uang
            keterangan: keterangan opsional
        Returns: transaksi_id atau None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO transaksi (user_id, tanggal, tipe, kategori, jumlah, keterangan)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, tanggal, tipe, kategori, jumlah, keterangan))
            
            transaksi_id = cursor.lastrowid
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return transaksi_id
            
        except Exception as e:
            print(f"Error create transaksi: {e}")
            return None
    
    @staticmethod
    def get_all_by_user(user_id, limit=None):
        """
        Dapatkan semua transaksi user
        Args:
            user_id: ID user
            limit: batasan jumlah data (opsional)
        Returns: list transaksi
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM transaksi 
                WHERE user_id = %s 
                ORDER BY tanggal DESC, created_at DESC
            """
            
            if limit:
                query += f" LIMIT {int(limit)}"
            
            cursor.execute(query, (user_id,))
            transaksi = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return transaksi
            
        except Exception as e:
            print(f"Error get transaksi: {e}")
            return []
    
    @staticmethod
    def get_filtered(user_id, kategori='', tanggal_mulai='', tanggal_akhir='', limit=None):
        """
        Dapatkan transaksi dengan filter
        Args:
            user_id: ID user
            kategori: filter kategori (opsional)
            tanggal_mulai: filter tanggal awal (opsional)
            tanggal_akhir: filter tanggal akhir (opsional)
            limit: batasan jumlah data (opsional)
        Returns: list transaksi
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM transaksi WHERE user_id = %s"
            params = [user_id]
            
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
            
            if limit:
                query += f" LIMIT {int(limit)}"
            
            cursor.execute(query, params)
            transaksi = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return transaksi
            
        except Exception as e:
            print(f"Error get filtered transaksi: {e}")
            return []
    
    @staticmethod
    def get_summary(user_id):
        """
        Dapatkan ringkasan transaksi user
        Args:
            user_id: ID user
        Returns: dict dengan pemasukan, pengeluaran, saldo
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Total pemasukan
            cursor.execute("""
                SELECT COALESCE(SUM(jumlah), 0) as total 
                FROM transaksi 
                WHERE user_id = %s AND tipe = 'Pemasukan'
            """, (user_id,))
            pemasukan = cursor.fetchone()['total']
            
            # Total pengeluaran (termasuk tabungan)
            cursor.execute("""
                SELECT COALESCE(SUM(jumlah), 0) as total 
                FROM transaksi 
                WHERE user_id = %s AND tipe IN ('Pengeluaran', 'Tabungan')
            """, (user_id,))
            pengeluaran = cursor.fetchone()['total']
            
            cursor.close()
            conn.close()
            
            return {
                'pemasukan': float(pemasukan),
                'pengeluaran': float(pengeluaran),
                'saldo': float(pemasukan) - float(pengeluaran),
                'arus_kas': float(pemasukan) - float(pengeluaran)
            }
            
        except Exception as e:
            print(f"Error get summary: {e}")
            return {
                'pemasukan': 0,
                'pengeluaran': 0,
                'saldo': 0,
                'arus_kas': 0
            }
    
    @staticmethod
    def get_by_kategori(user_id, tipe='Pengeluaran'):
        """
        Dapatkan transaksi dikelompokkan per kategori
        Args:
            user_id: ID user
            tipe: Pemasukan/Pengeluaran
        Returns: list dict dengan kategori dan total
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT kategori, SUM(jumlah) as total 
                FROM transaksi 
                WHERE user_id = %s AND tipe = %s
                GROUP BY kategori
            """, (user_id, tipe))
            
            hasil = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return hasil
            
        except Exception as e:
            print(f"Error get by kategori: {e}")
            return []
    
    @staticmethod
    def delete_all_by_user(user_id):
        """
        Hapus semua transaksi user (untuk reset data)
        Args:
            user_id: ID user
        Returns: Boolean
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM transaksi WHERE user_id = %s", (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error delete transaksi: {e}")
            return False
