from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, UserMixin, LoginManager

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

# Mock User Class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':
        return User(id='1')
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded credentials for testing
        if username == 'admin' and password == 'password':
            user = User(id='1')
            login_user(user)
            return redirect(url_for('hr.dashboard'))
        else:
            flash('Invalid credentials')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))