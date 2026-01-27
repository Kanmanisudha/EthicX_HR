import json
import os
import sys
from flask import Flask, request, jsonify
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# --- AUTOMATIC PATH FIXING ---
# This ensures the log file is always created in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "legal_audit_log.json")

@app.route('/')
def home():
    current_port = os.environ.get('FLASK_RUN_PORT', '5005')
    return {
        "status": "Online",
        "module": "06_INFRASTRUCTURE (Audit Logger)",
        "port": current_port,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.route('/log_decision', methods=['POST'])
def log_decision():
    """
    Receives decision data from Module 5 and archives it.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400
        
        # Create a structured legal record
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "audit_id": f"AUD-{int(datetime.utcnow().timestamp())}",
            "candidate_id": data.get("original_data", {}).get("candidate_id", "Unknown"),
            "candidate_name": data.get("original_data", {}).get("name", "Unknown"),
            "applied_role": data.get("original_data", {}).get("role", "Unknown"),
            "final_verdict": data.get("final_status", "UNKNOWN"),
            "risk_score": data.get("risk_score", 0),
            "ai_reasoning": data.get("ui_message", ""),
            "detected_strengths": data.get("key_factors", [])
        }

        print(f"\n📂 [Module 6] Archiving: {log_entry['candidate_name']}...")

        # --- SAFE FILE HANDLING ---
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        logs = json.loads(content)
            except (json.JSONDecodeError, IOError):
                print("⚠️ [Module 6] Log file corrupted or busy. Starting fresh list.")
                logs = []

        # Add new entry and save
        logs.append(log_entry)
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)

        print(f"✅ [Module 6] Saved. ID: {log_entry['audit_id']}")
        return jsonify({"status": "Archived", "audit_id": log_entry['audit_id']}), 200

    except Exception as e:
        print(f"❌ [Module 6] ERROR: {str(e)}")
        return jsonify({"error": "Failed to log decision"}), 500

if __name__ == '__main__':
    # Logic to capture the port from run_system.py or use default
    port_env = os.environ.get("FLASK_RUN_PORT", 5005)
    
    print("-" * 30)
    print(f"ETHICX AUDIT LOGGER STARTING")
    print(f"Target Port: {port_env}")
    print(f"Log Path: {LOG_FILE}")
    print("-" * 30)
    
    # host='0.0.0.0' is critical for microservices to communicate
    app.run(host="0.0.0.0", port=int(port_env), debug=False)