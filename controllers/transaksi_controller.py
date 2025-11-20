"""
TRANSAKSI CONTROLLER
"""
from models.transaksi import Transaksi
from models.tabungan import Tabungan

class TransaksiController:
    """Controller untuk transaksi"""
    
    @staticmethod
    def tambah_transaksi(user_id, data):
        """
        Tambah transaksi baru
        Args:
            user_id: ID user
            data: dict data transaksi
        Returns: tuple (success: Boolean, message: str)
        """
        try:
            transaksi_id = Transaksi.create(
                user_id=user_id,
                tanggal=data['tanggal'],
                tipe=data['tipe'],
                kategori=data['kategori'],
                jumlah=data['jumlah'],
                keterangan=data.get('keterangan', '')
            )
            
            if transaksi_id:
                return True, f"✅ {data['tipe']} berhasil ditambahkan!"
            else:
                return False, "❌ Gagal menambahkan transaksi"
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    @staticmethod
    def get_riwayat(user_id):
        """
        Dapatkan riwayat transaksi
        Args:
            user_id: ID user
        Returns: list transaksi
        """
        return Transaksi.get_all_by_user(user_id)
    
    @staticmethod
    def get_buku_besar(user_id, kategori='', tanggal_mulai='', tanggal_akhir='', limit=10):
        """
        Dapatkan data buku besar
        Args:
            user_id: ID user
            kategori: filter kategori
            tanggal_mulai: filter tanggal awal
            tanggal_akhir: filter tanggal akhir
            limit: batasan data
        Returns: dict dengan entries dan total
        """
        # Ambil transaksi filtered
        transaksi = Transaksi.get_filtered(
            user_id, kategori, tanggal_mulai, tanggal_akhir, limit
        )
        
        # Reverse untuk tampilan kronologis
        transaksi.reverse()
        
        # Format untuk buku besar
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
        
        return {
            'entries': entries,
            'total_debit': total_debit,
            'total_kredit': total_kredit,
            'saldo_akhir': total_debit - total_kredit
        }
