import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False) 
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Uploaded")
    risk_score = db.Column(db.Integer, default=50) 
    match_confidence = db.Column(db.Integer, default=0) 
    strengths = db.Column(db.String(500), default="")
    missing_skills = db.Column(db.String(500), default="Analysis Pending...") 
    ethics_status = db.Column(db.String(100), default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- AUTH SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

# --- FIXING BUILD ERRORS: ENDPOINTS ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('🚫 Invalid Credentials', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Resolves BuildError for endpoint 'signup'"""
    if request.method == 'POST':
        new_user = User(username=request.form['username'])
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/')
@login_required
def dashboard():
    candidates = Candidate.query.order_by(Candidate.timestamp.desc()).all()
    stats = {
        'total': len(candidates),
        'approved': len([c for c in candidates if "APPROVED" in str(c.status)]),
        'blocked': len([c for c in candidates if "BLOCKED" in str(c.status)]),
        'pending': len([c for c in candidates if "Uploaded" in str(c.status)])
    }
    return render_template('dashboard.html', candidates=candidates, stats=stats)

@app.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """Handles the Blue Upload Button"""
    file = request.files.get('resume')
    name = request.form.get('name')
    role = request.form.get('role')
    if file and name:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_candidate = Candidate(name=name, role=role, filename=filename)
        db.session.add(new_candidate)
        db.session.commit()
        flash(f'Candidate {name} uploaded!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_candidate/<int:c_id>')
@login_required
def delete_candidate(c_id):
    """Resolves BuildError for endpoint 'delete_candidate'"""
    candidate = Candidate.query.get_or_404(c_id)
    db.session.delete(candidate)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/reset_database')
@login_required
def reset_database():
    """Resolves BuildError for endpoint 'reset_database' (Flush Button)"""
    db.drop_all()
    db.create_all()
    admin = User(username='admin')
    admin.set_password('password')
    db.session.add(admin)
    db.session.commit()
    return redirect(url_for('dashboard'))

# --- AI PIPELINE ROUTE ---

@app.route('/action/<int:c_id>/<action_type>')
@login_required
def perform_action(c_id, action_type):
    candidate = Candidate.query.get(c_id)
    # This must match your Tier 2 Port (usually 5001)
    ORCHESTRATOR_URL = "http://127.0.0.1:5001/orchestrate/screening"
    
    payload = {
        "candidate_id": candidate.id,
        "role": candidate.role,
        "action": action_type,
        "requested_by": current_user.username
    }
    
    try:
        response = requests.post(ORCHESTRATOR_URL, json=payload, timeout=10)
        if response.status_code == 200:
            res = response.json()
            candidate.status = res.get('final_status', 'REVIEW')
            candidate.risk_score = res.get('risk_score', 0)
            candidate.match_confidence = max(0, 100 - candidate.risk_score)
            db.session.commit()
            flash('✅ AI Analysis Complete', 'success')
        else:
            flash(f'Backend Error: {response.status_code}', 'danger')
    except:
        flash('❌ Backend Offline: Ensure Tier 2 (Port 5001) is running.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)