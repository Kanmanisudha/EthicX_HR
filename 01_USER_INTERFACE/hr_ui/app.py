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
    role = db.Column(db.String(100), nullable=False) 
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="Uploaded")
    
    # --- ANALYTICS DATA ---
    risk_score = db.Column(db.Integer, default=50) 
    match_confidence = db.Column(db.Integer, default=0) 
    strengths = db.Column(db.String(500), default="") # e.g., "Python, Leadership"
    
    # NEW COLUMNS FOR "WHY" EXPLAINABILITY
    missing_skills = db.Column(db.String(500), default="") # e.g., "SysML, AWS"
    ethics_status = db.Column(db.String(100), default="Pending") # e.g., "Passed" / "Flagged"
    
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
        # Auto-create DB folder if missing
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
            print("✅ Default Admin Created (User: admin / Pass: password)")

# --- ROUTES ---
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
            flash('⚠️ User already exists.', 'warning')
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
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    candidates = Candidate.query.order_by(Candidate.timestamp.desc()).all()
    
    # 1. PROFESSIONAL HR METRICS
    total = len(candidates)
    approved = len([c for c in candidates if "APPROVED" in c.status])
    blocked = len([c for c in candidates if "BLOCKED" in c.status])
    # Any status that isn't Approved or Blocked counts as "Pending"
    pending = total - approved - blocked

    # 2. Package stats for the template
    stats = {
        'total': total,
        'approved': approved,
        'blocked': blocked,
        'pending': pending
    }

    return render_template('dashboard.html', candidates=candidates, stats=stats)

@app.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files: return redirect(url_for('dashboard'))
    file = request.files['resume']
    name = request.form.get('name')
    role = request.form.get('role')

    if file and name:
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Initialize new candidate with "Pending" analysis status
        new_candidate = Candidate(
            name=name, 
            role=role, 
            filename=filename, 
            risk_score=50, 
            match_confidence=0,
            missing_skills="Analysis Pending...",
            ethics_status="Pending"
        )
        db.session.add(new_candidate)
        db.session.commit()
        flash(f'📂 Candidate Added: {name}', 'info')

    return redirect(url_for('dashboard'))

# --- AI ORCHESTRATOR BRIDGE ---
@app.route('/action/<int:c_id>/<action_type>')
@login_required
def perform_action(c_id, action_type):
    candidate = Candidate.query.get(c_id)
    if not candidate: return redirect(url_for('dashboard'))

    orchestrator_url = "http://127.0.0.1:5001/orchestrate/screening"
    
    # Read File Content
    description_text = f"Candidate Name: {candidate.name}. Applied Role: {candidate.role}."
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                description_text += f" || FILE CONTENT: {f.read()[:5000]}"
    except Exception as e:
        print(f"File Read Error: {e}")

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
            
            # --- INTELLIGENCE EXTRACTION ---
            decision = result.get('final_status') or result.get('decision', 'UNKNOWN')
            score = result.get('risk_score', 0)
            msg = result.get('ui_message') or result.get('reason', '')
            positive_factors = result.get('key_factors', [])
            
            match_confidence = max(0, 100 - score)
            
            # --- SIMULATION LOGIC (To populate the UI Modals) ---
            # In a real production system, the AI module would return 'missing_skills' directly.
            # Here we simulate it based on the score so your UI looks active.
            
            missing_skills_list = []
            if match_confidence < 95: missing_skills_list.append("Advanced SysML")
            if match_confidence < 85: missing_skills_list.append("DO-178C Certification")
            if match_confidence < 70: missing_skills_list.append("Leadership Experience")
            if match_confidence < 60: missing_skills_list.append("Cloud Infrastructure (AWS)")
            
            missing_str = ", ".join(missing_skills_list) if missing_skills_list else "None Detected - Strong Match"
            
            # Ethics Check Simulation
            ethics_result = "Passed"
            if score > 75: # High risk implies potential issues
                ethics_result = "Flagged (Bias Risk)"

            # UPDATE DATABASE
            candidate.status = decision
            candidate.risk_score = score
            candidate.match_confidence = match_confidence
            candidate.strengths = ", ".join(positive_factors) if positive_factors else "General Engineering"
            candidate.missing_skills = missing_str
            candidate.ethics_status = ethics_result
            
            db.session.commit()

            if decision == "BLOCKED":
                flash(f"⛔ REJECTED: {msg}", 'danger')
            elif decision == "APPROVED":
                flash(f"✅ APPROVED ({match_confidence}% Match): {msg}", 'success')
            else:
                flash(f"⚠️ REVIEW: {msg}", 'warning')
        else:
            flash(f"❌ AI Error: Orchestrator returned {response.status_code}", 'danger')
            
    except requests.exceptions.ConnectionError:
        flash("❌ COMMUNICATION FAILURE: AI Module Offline. Run 'python ai_engine.py'", 'danger')

    return redirect(url_for('dashboard'))

@app.route('/delete/<int:c_id>')
@login_required
def delete_candidate(c_id):
    candidate = Candidate.query.get(c_id)
    if candidate:
        try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], candidate.filename))
        except: pass
        db.session.delete(candidate)
        db.session.commit()
        flash(f"🗑️ Record Deleted.", 'info')
    return redirect(url_for('dashboard'))

@app.route('/reset')
@login_required
def reset_database():
    try:
        db.session.query(Candidate).delete()
        db.session.commit()
        flash(f"🔄 Database Flushed.", 'warning')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    setup_database()
    print("🖥️  EthicX HR Dashboard Online - Port 5000")
    app.run(debug=True, port=5000)