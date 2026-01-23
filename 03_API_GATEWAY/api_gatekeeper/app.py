import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
# Connects to Module 4 (AI Engine)
AI_ENGINE_URL = "http://127.0.0.1:5002/analyze"

@app.route("/")
def home():
    return "EthicX Gatekeeper (Module 3) Online - Port 5004"

def inspect_payload(text):
    """
    Scans text for security threats.
    
    ADVANTAGES:
    1. BLOCKS SQL Injection (Prevents database hacking).
    2. BLOCKS SSNs (Prevents identity theft liability).
    3. ALLOWS Phone/Email (Enables recruiting).
    """
    
    # 1. BLOCK SQL INJECTION (Security Feature)
    # Detects malicious commands like "DROP TABLE" or "DELETE FROM"
    if re.search(r"drop\s+table|select\s+\*\s+from|delete\s+from|insert\s+into", text, re.IGNORECASE):
        return False, "BLOCKED", "Security Alert: Malicious SQL Injection detected."
    
    # 2. BLOCK SSN (Privacy Feature)
    # Detects Social Security Numbers (e.g., 123-45-6789)
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
        return False, "BLOCKED", "Security Alert: Restricted PII (SSN) detected."
    
    # 3. ALLOW PHONE & EMAIL (Recruiting Feature)
    # We explicitly return True here so resumes don't get blocked
    # This fixes the issue you were facing with Sarah Yeager's resume.
    return True, "SAFE", None

@app.route("/intercept", methods=["POST"])
def intercept():
    """
    Core Logic:
    - Scans incoming data.
    - If Safe -> Forwards to AI Engine (Module 4).
    - If Unsafe -> Returns BLOCKED response immediately.
    """
    try:
        data = request.json
        print(f"\n🛡️ [Gatekeeper] Scanning Candidate ID: {data.get('candidate_id')}...")
        
        # Combine text fields for scanning
        text_to_scan = str(data.get('description', '')) + " " + str(data.get('candidate_id', ''))
        
        # Run the inspection
        is_safe, decision, reason = inspect_payload(text_to_scan)

        if not is_safe:
            print(f"⛔ [Gatekeeper] BLOCKED! Reason: {reason}")
            # Return strict block to Orchestrator
            return jsonify({
                "final_status": "BLOCKED", 
                "risk_score": 100, 
                "ui_message": reason
            }), 200

        print("✅ [Gatekeeper] Content Safe. Forwarding to AI Engine...")
        
        try:
            # Forward safe data to Module 4
            response = requests.post(AI_ENGINE_URL, json=data)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.ConnectionError:
            print("❌ [Gatekeeper] Error: AI Engine (Port 5002) is down.")
            return jsonify({"ui_message": "System Error: AI Engine Offline"}), 503

    except Exception as e:
        print(f"❌ [Gatekeeper] Internal Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🛡️ API Gatekeeper running on Port 5004")
    app.run(host="127.0.0.1", port=5004, debug=True)