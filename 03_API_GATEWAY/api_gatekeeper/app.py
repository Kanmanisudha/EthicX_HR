import os
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Critical for allowing the Frontend (UI) to connect

# --- CONFIGURATION ---
# The Gatekeeper forwards data to the next module in the chain.
# Based on our previous flow, this is Module 5A (AI Engine) or 4A (Applicant)
AI_ENGINE_URL = "http://127.0.0.1:5002/analyze"

@app.route("/")
def home():
    current_port = os.environ.get('FLASK_RUN_PORT', 5000)
    return f"EthicX Gatekeeper (Module 3) Online - Port {current_port}"

def inspect_payload(text):
    """
    Nature: Scans text for security threats (SQLi) and privacy leaks (SSN).
    Advantages: Prevents database attacks and identity theft liability.
    """
    # 1. BLOCK SQL INJECTION
    sql_patterns = r"drop\s+table|select\s+\*\s+from|delete\s+from|insert\s+into"
    if re.search(sql_patterns, text, re.IGNORECASE):
        return False, "BLOCKED", "Security Alert: Malicious SQL Injection detected."
    
    # 2. BLOCK SSN (Sensitive PII)
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
        return False, "BLOCKED", "Security Alert: Restricted PII (SSN) detected."
    
    # 3. ALLOW PHONE & EMAIL (Recruiting Feature)
    return True, "SAFE", None

@app.route("/intercept", methods=["POST"])
def intercept():
    """
    Nature: The 'Entry Point' for the system. 
    If Safe -> Forwards to next service.
    If Unsafe -> Stops the request immediately.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        print(f"\n🛡️ [Gatekeeper] Scanning Candidate ID: {data.get('candidate_id', 'Unknown')}...")
        
        # Combine fields for a full security scan
        text_to_scan = f"{data.get('description', '')} {data.get('candidate_id', '')} {data.get('role', '')}"
        
        is_safe, decision, reason = inspect_payload(text_to_scan)

        if not is_safe:
            print(f"⛔ [Gatekeeper] BLOCKED! Reason: {reason}")
            return jsonify({
                "final_status": "BLOCKED", 
                "risk_score": 100, 
                "ui_message": reason
            }), 200 # Return 200 so the UI can display the message properly

        print("✅ [Gatekeeper] Content Safe. Forwarding to AI Engine...")
        
        try:
            # Cross-Service Call: Gateway -> AI Engine
            response = requests.post(AI_ENGINE_URL, json=data, timeout=10)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.ConnectionError:
            print("❌ [Gatekeeper] Error: AI Engine (Port 5002) is offline.")
            return jsonify({"ui_message": "System Error: AI Engine Offline"}), 503

    except Exception as e:
        print(f"❌ [Gatekeeper] Internal Error: {e}")
        return jsonify({"error": "Internal Gateway Error"}), 500

if __name__ == "__main__":
    # Gateway usually runs on Port 5000 as the main entry point
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    print(f"🛡️ API Gatekeeper active on Port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)