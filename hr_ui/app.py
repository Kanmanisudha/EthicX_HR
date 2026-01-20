import os
import requests
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# --- INITIALIZE DATABASE ---
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False) # Stores the specific role profile
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Uploaded")
    risk_score = db.Column(db.Integer, default=50) # Default neutral
    match_confidence = db.Column(db.Integer, default=0) # NEW: "Match %" for High Tech UI
    strengths = db.Column(db.String(500), default="") 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- SETUP AUTH ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATABASE SETUP ---
def setup_database():
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_folder = os.path.dirname(db_path)
            if not os.path.exists(db_folder):
                os.makedirs(db_folder)
        
        db.create_all()
        # Create Default Admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('🚫 Access Denied: Invalid Credentials', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('⚠️ User already exists in system registry.', 'warning')
            return redirect(url_for('signup'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('✅ User Registered. Initialize Login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- HIGH TECH DASHBOARD ---
@app.route('/')
@login_required
def dashboard():
    candidates = Candidate.query.order_by(Candidate.timestamp.desc()).all()
    
    # 1. Pipeline Stats
    total = len(candidates)
    approved = len([c for c in candidates if "APPROVED" in c.status])
    blocked = len([c for c in candidates if "BLOCKED" in c.status])
    pending = total - approved - blocked

    # 2. System Health (High Tech Flavor)
    threat_level = "LOW"
    integrity = 100
    if blocked > 0:
        threat_level = "ELEVATED"
        integrity = max(50, 100 - (blocked * 5))
    if blocked > 5:
        threat_level = "CRITICAL"
        integrity = 30
    
    system_status = {
        "status": "ONLINE",
        "modules_active": 6,
        "threat_level": threat_level,
        "integrity": f"{integrity}%",
        "uptime": "99.9%"
    }

    return render_template('dashboard.html', 
                           candidates=candidates, 
                           stats={'total': total, 'approved': approved, 'blocked': blocked, 'pending': pending},
                           system=system_status)

@app.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files: return redirect(url_for('dashboard'))
    file = request.files['resume']
    name = request.form.get('name')
    role = request.form.get('role') # Now captures exact string from Dropdown

    if file and name:
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Initialize with Neutral Score
        new_candidate = Candidate(name=name, role=role, filename=filename, risk_score=50, match_confidence=0)
        db.session.add(new_candidate)
        db.session.commit()
        flash(f'📂 Uplink Established: {name} added to queue for {role}.', 'info')

    return redirect(url_for('dashboard'))

# --- AI ACTION CENTER ---
@app.route('/action/<int:c_id>/<action_type>')
@login_required
def perform_action(c_id, action_type):
    candidate = Candidate.query.get(c_id)
    if not candidate: return redirect(url_for('dashboard'))

    # ORCHESTRATOR CONNECTION (Module 2)
    orchestrator_url = "http://127.0.0.1:5001/orchestrate/screening"
    
    # Read File Content
    description_text = f"Candidate Name: {candidate.name}. Applied Role: {candidate.role}."
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.filename)
        if os.path.exists(file_path):
            valid_extensions = ('.cpp', '.c', '.py', '.java', '.txt', '.md', '.json', '.html')
            if candidate.filename.lower().endswith(valid_extensions):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    description_text += f" || FILE CONTENT: {f.read()[:5000]}"
    except Exception as e:
        print(f"File Read Error: {e}")

    # PAYLOAD: Strictly includes Name & Role for Profile-Based Scoring
    payload = {
        "candidate_id": candidate.id,
        "name": candidate.name,  
        "role": candidate.role,  
        "action": action_type,
        "description": description_text,
        "requested_by": current_user.username
    }
    
    try:
        response = requests.post(orchestrator_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract AI Data
            decision = result.get('final_status') or result.get('decision', 'UNKNOWN')
            score = result.get('risk_score', 0)
            msg = result.get('ui_message') or result.get('reason', '')
            positive_factors = result.get('key_factors', [])
            
            # Convert Risk Score to "Match Confidence" (0 Risk = 100% Match)
            match_confidence = max(0, 100 - score)

            # Update DB
            candidate.status = decision
            candidate.risk_score = score
            candidate.match_confidence = match_confidence
            candidate.strengths = ", ".join(positive_factors) if positive_factors else "None Detected"
            db.session.commit()

            # Feedback Messages
            if decision == "BLOCKED":
                flash(f"⛔ SECURITY ALERT: {msg}", 'danger')
            elif decision == "APPROVED":
                flash(f"✅ MATCH CONFIRMED ({match_confidence}%): {msg}", 'success')
            else:
                flash(f"⚠️ REVIEW REQUIRED: {msg}", 'warning')
        else:
            flash(f"❌ SYSTEM ERROR: Orchestrator returned {response.status_code}", 'danger')
            
    except requests.exceptions.ConnectionError:
        flash("❌ COMMUNICATION FAILURE: Modules Offline.", 'danger')

    return redirect(url_for('dashboard'))

@app.route('/delete/<int:c_id>')
@login_required
def delete_candidate(c_id):
    candidate = Candidate.query.get(c_id)
    if candidate:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], candidate.filename))
        except: pass
        db.session.delete(candidate)
        db.session.commit()
        flash(f"🗑️ Data Purged: Candidate removed.", 'info')
    return redirect(url_for('dashboard'))

@app.route('/reset')
@login_required
def reset_database():
    try:
        db.session.query(Candidate).delete()
        db.session.commit()
        flash(f"🔄 SYSTEM RESET: Database flushed.", 'warning')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    setup_database()
    print("🖥️  EthicX High-Tech Dashboard Online - Port 5000")
    app.run(debug=True, port=5000)