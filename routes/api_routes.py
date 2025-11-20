"""
API ROUTES
"""
from flask import Blueprint, request, jsonify, session, send_file
from utils.decorators import login_required, save_uploaded_file
from controllers.dashboard_controller import DashboardController
from controllers.transaksi_controller import TransaksiController
from controllers.profil_controller import ProfilController
from models.tabungan import Tabungan
from models.transaksi import Transaksi

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ===== DASHBOARD APIS =====
@api_bp.route('/summary', methods=['GET'])
@login_required
def get_summary():
    """API untuk mendapatkan summary data"""
    user_id = session.get('user_id')
    data = DashboardController.get_summary_data(user_id)
    return jsonify(data)

@api_bp.route('/chart-data', methods=['GET'])
@login_required
def get_chart_data():
    """API untuk mendapatkan data chart"""
    user_id = session.get('user_id')
    data = DashboardController.get_chart_data(user_id)
    return jsonify(data)

# ===== TRANSAKSI APIS =====
@api_bp.route('/transaksi', methods=['POST'])
@login_required
def tambah_transaksi():
    """API untuk menambah transaksi"""
    user_id = session.get('user_id')
    data = request.json
    
    success, message = TransaksiController.tambah_transaksi(user_id, data)
    return jsonify({'success': success, 'message': message})

@api_bp.route('/riwayat', methods=['GET'])
@login_required
def get_riwayat():
    """API untuk mendapatkan riwayat transaksi"""
    user_id = session.get('user_id')
    riwayat = TransaksiController.get_riwayat(user_id)
    return jsonify(riwayat)

@api_bp.route('/buku-besar', methods=['GET'])
@login_required
def get_buku_besar():
    """API untuk mendapatkan buku besar"""
    user_id = session.get('user_id')
    
    kategori = request.args.get('kategori', '')
    tanggal_mulai = request.args.get('tanggal_mulai', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    limit = request.args.get('limit', 10)
    
    data = TransaksiController.get_buku_besar(
        user_id, kategori, tanggal_mulai, tanggal_akhir, limit
    )
    
    return jsonify(data)

# ===== TABUNGAN APIS =====
@api_bp.route('/tabungan', methods=['GET'])
@login_required
def get_tabungan():
    """API untuk mendapatkan saldo tabungan"""
    user_id = session.get('user_id')
    jumlah = Tabungan.get_by_user(user_id)
    return jsonify({'jumlah': jumlah})

@api_bp.route('/tabungan/kelola', methods=['POST'])
@login_required
def kelola_tabungan():
    """API untuk mengelola tabungan (tambah/ambil)"""
    user_id = session.get('user_id')
    data = request.json
    
    aksi = data.get('aksi')
    jumlah = float(data.get('jumlah'))
    
    # Cek saldo tersedia
    summary = Transaksi.get_summary(user_id)
    saldo_tersedia = summary['saldo']
    
    if aksi == 'tambah':
        # Cek apakah saldo tersedia cukup
        if jumlah > saldo_tersedia:
            return jsonify({
                'success': False, 
                'message': f'❌ Saldo tersedia tidak cukup! Anda hanya punya Rp {saldo_tersedia:,.0f}'
            })
        
        # Tambah ke tabungan
        Tabungan.tambah(user_id, jumlah)
        
        # Catat sebagai transaksi Tabungan (kredit)
        Transaksi.create(
            user_id=user_id,
            tanggal='CURDATE()',
            tipe='Tabungan',
            kategori='Tabungan',
            jumlah=jumlah,
            keterangan='Menabung'
        )
        
        return jsonify({
            'success': True,
            'message': f'✅ Berhasil menambah Rp {jumlah:,.0f} ke tabungan!'
        })
    
    else:  # ambil
        success, message = Tabungan.kurang(user_id, jumlah)
        
        if not success:
            return jsonify({'success': False, 'message': f'❌ {message}'})
        
        # Catat sebagai transaksi Pemasukan (debit)
        Transaksi.create(
            user_id=user_id,
            tanggal='CURDATE()',
            tipe='Pemasukan',
            kategori='Tabungan',
            jumlah=jumlah,
            keterangan='Ambil dari tabungan'
        )
        
        return jsonify({
            'success': True,
            'message': f'✅ Berhasil mengambil Rp {jumlah:,.0f} dari tabungan!'
        })

# ===== PROFIL APIS =====
@api_bp.route('/profil/update', methods=['POST'])
@login_required
def update_profil():
    """API untuk update profil"""
    user_id = session.get('user_id')
    data = request.json
    
    success, message = ProfilController.update_profil(user_id, data)
    return jsonify({'success': success, 'message': message})

@api_bp.route('/profil/reset-password', methods=['POST'])
@login_required
def reset_password():
    """API untuk reset password"""
    user_id = session.get('user_id')
    data = request.json
    
    success, message = ProfilController.update_password(
        user_id,
        data.get('current_password'),
        data.get('new_password'),
        data.get('new_password')  # confirm sama dengan new
    )
    
    return jsonify({'success': success, 'message': message})

@api_bp.route('/profil/upload-foto', methods=['POST'])
@login_required
def upload_foto():
    """API untuk upload foto profil"""
    user_id = session.get('user_id')
    
    if 'foto' not in request.files:
        return jsonify({'success': False, 'message': 'Tidak ada file yang diupload'})
    
    file = request.files['foto']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih'})
    
    # Simpan file
    photo_url = save_uploaded_file(file, user_id)
    
    if not photo_url:
        return jsonify({'success': False, 'message': 'Format file tidak didukung. Gunakan PNG, JPG, atau JPEG'})
    
    # Update database
    success, message = ProfilController.update_foto(user_id, photo_url)
    
    if success:
        return jsonify({'success': True, 'message': message, 'foto_url': photo_url})
    else:
        return jsonify({'success': False, 'message': message})

@api_bp.route('/profil/reset-data', methods=['POST'])
@login_required
def reset_data():
    """API untuk reset semua data keuangan"""
    user_id = session.get('user_id')
    data = request.json
    
    password = data.get('password')
    
    if not password:
        return jsonify({'success': False, 'message': '❌ Password tidak boleh kosong!'})
    
    success, message = ProfilController.reset_data(user_id, password)
    return jsonify({'success': success, 'message': message})
