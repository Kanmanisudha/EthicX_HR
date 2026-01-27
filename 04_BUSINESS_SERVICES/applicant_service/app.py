import sys
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# --- PATH CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ensuring the service can find its local 'logic.py'
sys.path.append(current_dir)

try:
    # This imports your PDF extraction and scoring features
    from logic import extract_text_from_pdf, calculate_score
except ImportError:
    print("⚠️ Warning: logic.py not found in applicant_service folder. Scoring will fail.")

app = Flask(__name__)
CORS(app) # Enables the UI to talk to this service

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
THRESHOLD_SCORE = 70

# --- MICROSERVICE TARGETS ---
# In a true microservice, we send sanitized text to the Sanitizer module (Port 5002)
SANITIZER_URL = "http://127.0.0.1:5002/sanitize"

@app.route('/')
def home():
    # Nature: Serves the intake form/login
    return render_template('login.html') 

@app.route('/submit-resume', methods=['POST'])
def submit_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    role = request.form.get('role', 'General Avionics')
    candidate_id = request.form.get('candidate_id', 'CAND-99')

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # A. PARSE (Using your existing feature)
        print(f"📄 [4A] Extracting text from: {file.filename}")
        resume_text = extract_text_from_pdf(file)
        
        # B. SCORE (Initial screening)
        dummy_keywords = ["python", "java", "sql", "ethics", "communication"]
        score, report = calculate_score(resume_text, dummy_keywords)
        
        # C. CHAINING: Send to Sanitizer Module (Port 5002)
        # This follows the 'Pipes and Filters' nature of your project
        payload = {
            "candidate_id": candidate_id,
            "role": role,
            "description": resume_text,
            "initial_score": score
        }
        
        print("🧼 [4A] Forwarding to Sanitizer (Port 5002)...")
        try:
            # We don't stop if sanitizer fails, but we try to use it
            san_res = requests.post(SANITIZER_URL, json=payload, timeout=3)
            final_payload = san_res.json().get('sanitized_data', payload)
        except:
            print("⚠️ Sanitizer offline. Using raw text.")
            final_payload = payload

        # D. FINAL RESPONSE (Shortlist check)
        if score >= THRESHOLD_SCORE:
            return jsonify({
                "status": "SHORTLISTED",
                "message": "Congratulations! Your profile has been forwarded to HR.",
                "score": score,
                "data_transmitted": True
            })
        else:
            return jsonify({
                "status": "REJECTED_WITH_FEEDBACK",
                "message": "Application not moved forward due to score thresholds.",
                "transparency_report": report,
                "score": score
            })

    except Exception as e:
        print(f"❌ [4A] Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Dynamically pick up port 5001 from run_system.py
    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    print(f"🚀 Applicant Service active on Port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)