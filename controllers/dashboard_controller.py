"""
DASHBOARD CONTROLLER
"""
from models.transaksi import Transaksi
from models.tabungan import Tabungan

class DashboardController:
    """Controller untuk dashboard"""
    
    @staticmethod
    def get_summary_data(user_id):
        """
        Dapatkan data summary untuk dashboard
        Args:
            user_id: ID user
        Returns: dict summary data
        """
        # Ambil summary transaksi
        summary = Transaksi.get_summary(user_id)
        
        # Ambil saldo tabungan
        tabungan = Tabungan.get_by_user(user_id)
        
        # Hitung health score
        health_score = DashboardController.calculate_health_score(summary, tabungan)
        
        return {
            'pemasukan': summary['pemasukan'],
            'pengeluaran': summary['pengeluaran'],
            'saldo': summary['saldo'],
            'arus_kas': summary['arus_kas'],
            'tabungan': tabungan,
            'health_score': health_score
        }
    
    @staticmethod
    def get_chart_data(user_id):
        """
        Dapatkan data untuk chart
        Args:
            user_id: ID user
        Returns: dict chart data
        """
        # Data untuk pie chart (pengeluaran per kategori)
        kategori_data = Transaksi.get_by_kategori(user_id, 'Pengeluaran')
        
        kategori_labels = [item['kategori'] for item in kategori_data]
        kategori_values = [float(item['total']) for item in kategori_data]
        
        # Data untuk bar chart
        summary = Transaksi.get_summary(user_id)
        tabungan = Tabungan.get_by_user(user_id)
        
        return {
            'kategori_labels': kategori_labels,
            'kategori_values': kategori_values,
            'pemasukan': summary['pemasukan'],
            'pengeluaran': summary['pengeluaran'],
            'saldo': summary['saldo'],
            'tabungan': tabungan
        }
    
    @staticmethod
    def calculate_health_score(summary, tabungan):
        """
        Hitung health score keuangan
        Args:
            summary: dict summary transaksi
            tabungan: float saldo tabungan
        Returns: int (0-100)
        """
        score = 50  # Base score
        
        pemasukan = summary['pemasukan']
        pengeluaran = summary['pengeluaran']
        saldo = summary['saldo']
        
        # Tabungan factor (max +20)
        if tabungan > 0 and pemasukan > 0:
            tabungan_ratio = tabungan / pemasukan
            score += min(20, tabungan_ratio * 100)
        
        # Saldo factor (max +15)
        if saldo > 0 and pemasukan > 0:
            saldo_ratio = saldo / pemasukan
            score += min(15, saldo_ratio * 50)
        elif saldo < 0:
            score -= 15
        
        # Arus kas factor (max +10)
        if saldo > 0:
            score += 10
        else:
            score -= 10
        
        # Pengeluaran ratio factor (max +5)
        if pemasukan > 0:
            pengeluaran_ratio = pengeluaran / pemasukan
            if pengeluaran_ratio < 0.5:
                score += 5
            elif pengeluaran_ratio > 0.9:
                score -= 10
        
        return max(0, min(100, round(score)))
