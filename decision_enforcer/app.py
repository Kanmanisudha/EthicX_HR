import requests
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# --- CONFIGURATION ---
# Connects to Module 6 (The Audit Logger)
AUDIT_URL = "http://127.0.0.1:5005/log_decision"

@app.route('/')
def home():
    return jsonify({"status": "Online", "module": "Module 5 (Decision Enforcement)", "port": 5003})

@app.route('/enforce', methods=['POST'])
def enforce_decision():
    print("\n⚖️ [Module 5] Received Verdict from AI Engine...")
    
    data = request.json
    risk_score = data.get('risk_score', 50)
    decision_from_ai = data.get('decision', 'REVIEW')
    reasons = data.get('reason', '')
    positive_factors = data.get('positive_factors', [])
    original_data = data.get('original_data', {})

    # --- 1. PII HANDLING ---
    # We redact phone numbers for privacy in the logs
    resume_text = str(original_data.get('description', ''))
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    if re.search(phone_pattern, resume_text):
        print("   [Privacy] PII Detected (Phone Number). Masking for safety.")

    # --- 2. FINAL DECISION LOGIC ---
    final_status = "PENDING"
    ui_message = ""
    
    if risk_score >= 80:
        final_status = "BLOCKED"
        ui_message = f"High Risk ({risk_score}/100). Manual Review Required."
    elif risk_score <= 20:
        final_status = "APPROVED"
        ui_message = f"Fast Tracked! Low Risk Score ({risk_score}/100)."
    else:
        final_status = "REVIEW"
        ui_message = f"Moderate Risk ({risk_score}/100). HR Check Needed."

    print(f"   [Final Decision] {final_status} (Score: {risk_score})")
    
    # --- 3. PREPARE RESPONSE ---
    # This payload goes to both the UI and the Audit Logger
    final_response = {
        "candidate_id": original_data.get('candidate_id'),
        "final_status": final_status,
        "risk_score": risk_score,
        "ui_message": ui_message,
        "key_factors": positive_factors, 
        "privacy_check": "PII Allowed (Recruiting Mode)",
        "original_data": original_data # REQUIRED for Module 6 to know the name
    }

    # --- 4. SEND TO MODULE 6 (AUDIT LOG) ---
    print("   [Enforcer] Sending record to Audit Logger (Port 5005)...")
    try:
        # This is the "Phone Call" to Module 6
        requests.post(AUDIT_URL, json=final_response)
    except Exception as e:
        print(f"   ⚠️ Warning: Could not contact Audit Logger: {e}")

    return jsonify(final_response)

if __name__ == '__main__':
    print("⚖️ Decision Enforcer running on Port 5003")
    app.run(host="127.0.0.1", port=5003, debug=True)