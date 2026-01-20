import os
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from services.api_client import WebOperatingLayerClient

hr_bp = Blueprint('hr', __name__)

# --- IN-MEMORY DATABASE (Resets when you restart the server) ---
candidates = [
    {"id": 101, "name": "Alice Johnson", "role": "Software Engineer", "status": "Pending", "filename": "alice_cv.pdf"},
    {"id": 102, "name": "Bob Smith", "role": "Data Analyst", "status": "Pending", "filename": "bob_cv.pdf"}
]

@hr_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', candidates=candidates)

@hr_bp.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    # 1. Check if file is present
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(url_for('hr.dashboard'))
    
    file = request.files['resume']
    name = request.form.get('name')  # Get Name from form
    role = request.form.get('role')  # Get Role from form

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('hr.dashboard'))
        
    if file and name and role:
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file
        file.save(save_path)
        
        # --- CRITICAL FIX: Add to the list ---
        new_id = candidates[-1]['id'] + 1 if candidates else 101
        new_candidate = {
            "id": new_id,
            "name": name,
            "role": role,
            "status": "Uploaded",
            "filename": filename
        }
        candidates.append(new_candidate)
        # -------------------------------------

        flash(f'Candidate {name} added and resume uploaded successfully!')
        
    return redirect(url_for('hr.dashboard'))

@hr_bp.route('/action/<int:candidate_id>/<action_type>')
@login_required
def perform_action(candidate_id, action_type):
    # Find the candidate to show their name in the message
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    
    if not candidate:
        flash("Candidate not found.")
        return redirect(url_for('hr.dashboard'))

    # Call Module 2 (Mocked)
    result = WebOperatingLayerClient.send_action(candidate_id, action_type)
    
    # Update status locally for UI feedback
    candidate['status'] = f"{action_type} ({result.get('ethical_decision')})"
    
    flash(f"Action: {action_type} for {candidate['name']} | Decision: {result.get('ethical_decision')} | Reason: {result.get('message')}")
    return redirect(url_for('hr.dashboard'))