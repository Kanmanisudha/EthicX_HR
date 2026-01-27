import os
import re
import sys
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
# Connects to Module 6 (The Infrastructure Audit Logger)
AUDIT_URL = "http://127.0.0.1:5005/log_decision"

# --- 1. PRIVACY & SECURITY HELPERS ---

def mask_pii_data(text):
    """
    Nature: Scans for sensitive information (Phone Numbers) 
    and masks them to ensure privacy in the system logs.
    """
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    if re.search(phone_pattern, text):
        return re.sub(phone_pattern, "[REDACTED PHONE]", text), True
    return text, False

# --- 2. CORE DECISION LOGIC ---

def determine_final_status(risk_score):
    """
    Nature: Translates a numerical risk score into a human-readable 
    hiring verdict used by the User Interface.
    """
    if risk_score >= 80:
        return "BLOCKED", f"🔴 High Risk ({risk_score}/100). Ethical markers or skill gap detected."
    elif 20 < risk_score < 80:
        return "REVIEW", f"🟡 Moderate Risk ({risk_score}/100). Requires manual HR validation."
    elif risk_score <= 20:
        return "APPROVED", f"🟢 Low Risk ({risk_score}/100). Candidate meets all critical criteria."
    return "PENDING", "Status evaluation incomplete."

# --- 3. API ENDPOINTS ---

@app.route('/')
def health_check():
    return jsonify({
        "module": "05B_DECISION_ENFORCER",
        "status": "Ready",
        "enforcement_rules": "Active",
        "privacy_filter": "Enabled"
    })

@app.route('/enforce', methods=['POST'])
def enforce():
    start_time = time.time()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No decision data received from Module 5A"}), 400

    print("\n⚖️ [5B] Enforcing Final Decision for Candidate...")

    # Extract data from Module 5A
    risk_score = data.get('risk_score', 50)
    reasons = data.get('reason', '')
    positive_factors = data.get('positive_factors', [])
    original_data = data.get('original_data', {})

    # 1. PRIVACY CHECK (PII Redaction)
    description = str(original_data.get('description', ''))
    clean_desc, pii_found = mask_pii_data(description)
    if pii_found:
        print("🔒 [5B] Privacy Alert: PII detected and masked in audit trail.")

    # 2. APPLY ENFORCEMENT RULES
    final_status, ui_message = determine_final_status(risk_score)
    
    # 3. CONSTRUCT AUDIT PAYLOAD
    # This matches the structure expected by Module 06
    audit_payload = {
        "final_status": final_status,
        "risk_score": risk_score,
        "ui_message": ui_message,
        "key_factors": positive_factors,
        "original_data": {
            **original_data,
            "description": clean_desc # Send the masked version to the logs
        }
    }

    # 4. COMMUNICATE WITH MODULE 06 (INFRASTRUCTURE)
    print(f"📡 [5B] Sending Record to Audit Logger (Port 5005). Status: {final_status}")
    try:
        # We forward the audit_payload to the Logger
        audit_res = requests.post(AUDIT_URL, json=audit_payload, timeout=3)
        audit_status = "Archived" if audit_res.status_code == 200 else "Failed to Archive"
    except Exception as e:
        print(f"⚠️ [5B] Audit Logger Error: {e}")
        audit_status = "Offline"

    # 5. FINAL RESPONSE TO THE CALLER (Usually Module 04 or 03)
    response_package = {
        **audit_payload,
        "audit_status": audit_status,
        "enforcement_time_ms": round((time.time() - start_time) * 1000, 2)
    }

    print(f"✅ [5B] Enforcement Complete. Final Verdict: {final_status}")
    return jsonify(response_package)

if __name__ == '__main__':
    # Listen on Port 5003 (Synced with EthicX Engine and Orchestrator)
    port = int(os.environ.get("FLASK_RUN_PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=False)