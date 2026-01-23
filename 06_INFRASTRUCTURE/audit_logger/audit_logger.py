import json
import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
# This file will be created in your project folder
LOG_FILE = "legal_audit_log.json"

@app.route('/')
def home():
    return "EthicX Audit Logger (Module 6) Online - Port 5005"

@app.route('/log_decision', methods=['POST'])
def log_decision():
    """
    Receives the FINAL DECISION from Module 5.
    Saves it to a permanent JSON file for legal compliance.
    """
    try:
        data = request.json
        
        # Create a structured, timestamped legal record
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z", # Z indicates UTC
            "audit_id": f"AUD-{int(datetime.utcnow().timestamp())}",
            "candidate_id": data.get("original_data", {}).get("candidate_id", "Unknown"),
            "candidate_name": data.get("original_data", {}).get("name", "Unknown"),
            "applied_role": data.get("original_data", {}).get("role", "Unknown"),
            "final_verdict": data.get("final_status", "UNKNOWN"),
            "risk_score": data.get("risk_score", 0),
            "ai_reasoning": data.get("ui_message", ""),
            "detected_strengths": data.get("key_factors", [])
        }

        print(f"\n📂 [Module 6] Archiving Decision for Candidate: {log_entry['candidate_name']}...")

        # --- FILE HANDLING LOGIC ---
        # 1. Read existing logs (if file exists)
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r') as f:
                    # Check if file is empty to avoid JSON errors
                    content = f.read()
                    if content.strip():
                        logs = json.loads(content)
            except json.JSONDecodeError:
                print("⚠️ [Module 6] Warning: Log file was corrupted. Starting fresh.")
                logs = [] # Reset if corrupt

        # 2. Append the new decision
        logs.append(log_entry)

        # 3. Save back to file (Write mode)
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)

        print(f"✅ [Module 6] Decision Saved. Log ID: {log_entry['audit_id']}")
        return jsonify({"status": "Archived", "audit_id": log_entry['audit_id']}), 200

    except Exception as e:
        print(f"❌ [Module 6] CRITICAL LOGGING ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("📂 Audit Logger running on Port 5005")
    app.run(host="127.0.0.1", port=5005)