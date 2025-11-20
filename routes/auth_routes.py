"""
AUTHENTICATION ROUTES
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route untuk login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, message, user_id = AuthController.login(username, password)
        
        if success:
            return redirect(url_for('web.index'))
        else:
            return render_template('login.html', 
                                 title='Login', 
                                 is_register=False, 
                                 error=message)
    
    return render_template('login.html', title='Login', is_register=False)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Route untuk register"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        success, message = AuthController.register(username, email, password, confirm_password)
        
        if success:
            return render_template('login.html', 
                                 title='Register', 
                                 is_register=True, 
                                 success=message)
        else:
            return render_template('login.html', 
                                 title='Register', 
                                 is_register=True, 
                                 error=message)
    
    return render_template('login.html', title='Register', is_register=True)

@auth_bp.route('/logout')
def logout():
    """Route untuk logout"""
    AuthController.logout()
    return redirect(url_for('auth.login'))
