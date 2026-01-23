import sys
import os
from flask import Flask, request, jsonify, render_template

# --- ARCHITECTURE FIX: Add Parent Folders to Path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../')) 

# Add the specific layers we need to import from
sys.path.append(os.path.join(project_root, '05_CORE_ENGINE'))
sys.path.append(os.path.join(project_root, '06_INFRASTRUCTURE'))

# Import your local logic (Make sure logic.py exists in this folder)
try:
    from logic import extract_text_from_pdf, calculate_score
except ImportError:
    print("Warning: logic.py not found. Scoring will fail.")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
THRESHOLD_SCORE = 70

@app.route('/')
def home():
    return render_template('login.html') 

@app.route('/submit-resume', methods=['POST'])
def submit_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # A. PARSE
        resume_text = extract_text_from_pdf(file)
        
        # B. SCORE
        dummy_keywords = ["python", "java", "sql", "ethics", "communication"]
        score, report = calculate_score(resume_text, dummy_keywords)
        
        # C. DECISION
        if score >= THRESHOLD_SCORE:
            return jsonify({
                "status": "SHORTLISTED",
                "message": "Congratulations! Your profile has been forwarded to HR.",
                "score": score
            })
        else:
            return jsonify({
                "status": "REJECTED_WITH_FEEDBACK",
                "message": "Application not moved forward.",
                "transparency_report": report 
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Applicant Service running on http://localhost:5001")
    app.run(port=5001, debug=True)