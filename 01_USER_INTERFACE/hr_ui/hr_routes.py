import os
import requests
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, Candidate  # Importing from main app to share context
from config import Config

# Create a Blueprint for HR-specific routes
hr_bp = Blueprint('hr_routes', __name__)

@hr_bp.route('/hr/dashboard')
@login_required
def dashboard():
    """Nature: Fetches all candidates and renders the main management console."""
    candidates = Candidate.query.order_by(Candidate.timestamp.desc()).all()
    
    # Calculate HR Metrics for the Dashboard
    stats = {
        'total': len(candidates),
        'approved': len([c for c in candidates if c.status == "APPROVED"]),
        'blocked': len([c for c in candidates if c.status == "BLOCKED"]),
        'pending': len([c for c in candidates if c.status not in ["APPROVED", "BLOCKED"]])
    }
    
    return render_template('dashboard.html', candidates=candidates, stats=stats)

@hr_bp.route('/hr/analyze/<int:candidate_id>')
@login_required
def analyze_candidate(candidate_id):
    """
    Nature: This is the trigger point for the 6-tier microservice chain.
    It takes a candidate from the UI DB and 'fires' it at the Orchestrator.
    """
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Construct the standard payload for the Web Operating Layer (Port 5001)
    payload = {
        "candidate_id": candidate.id,
        "name": candidate.name,
        "role": candidate.role,
        "action": "ETHICAL_SCREENING",
        "requested_by": current_user.username,
        "description": f"Target Role: {candidate.role}. Resume Reference: {candidate.filename}"
    }

    print(f"📡 [HR_ROUTES] Triggering analysis for Candidate {candidate.id}...")

    try:
        # Call Module 02: Web Operating Layer
        response = requests.post(Config.ORCHESTRATOR_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # Nature: Update the UI Database with findings from the backend chain
            candidate.status = result.get('final_status', 'REVIEW')
            candidate.risk_score = result.get('risk_score', 50)
            candidate.ethics_status = "Passed" if candidate.risk_score < 75 else "Flagged"
            
            db.session.commit()
            flash(f"✅ Analysis for {candidate.name} completed successfully.", "success")
        else:
            flash(f"⚠️ Backend Error: {response.status_code}", "warning")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ [HR_ROUTES] Connection Failure: {e}")
        flash("❌ Backend Orchestrator (Port 5001) is offline.", "danger")

    return redirect(url_for('hr_routes.dashboard'))

@hr_bp.route('/hr/delete/<int:candidate_id>')
@login_required
def delete_candidate(candidate_id):
    """Nature: Clean up local candidate records."""
    candidate = Candidate.query.get_or_404(candidate_id)
    db.session.delete(candidate)
    db.session.commit()
    flash(f"🗑️ Record for {candidate.name} removed.", "info")
    return redirect(url_for('hr_routes.dashboard'))