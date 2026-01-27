import os
import uuid
import requests
from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows the UI to connect to this orchestrator

# --- CONFIGURATION ---
# Connects to Module 3 (Gatekeeper)
# Ensure this matches the Gatekeeper's port in your run_system.py
GATEKEEPER_URL = "http://127.0.0.1:5000/intercept" 

@app.route("/")
def home():
    current_port = os.environ.get('FLASK_RUN_PORT', 5001)
    return f"EthicX-HR Web Operating Layer (Module 2) active on Port {current_port}"

@app.route("/orchestrate/screening", methods=["POST"])
def orchestrate_screening():
    """
    Nature: The 'System Brain' for data flow. 
    It assigns tracking IDs and standardizes data before security checks.
    """
    try:
        incoming_request = request.json
        if not incoming_request:
            return jsonify({"error": "No data provided"}), 400

        print(f"\n📥 [Module 2] Orchestrating Request for Candidate: {incoming_request.get('candidate_id', 'Unknown')}")

        # FEATURE: Legal Audit Trail (UUID Generation)
        orchestration_id = str(uuid.uuid4())
        
        # FEATURE: Data Standardization
        # We wrap the UI data in a formal system packet
        standardized_payload = {
            "orchestration_id": orchestration_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "origin": "HR_PORTAL_WEB",
            "candidate_id": incoming_request.get("candidate_id"),
            "role": incoming_request.get("role"),
            "action_type": incoming_request.get("action", "SCREENING"),
            "requested_by": incoming_request.get("requested_by", "HR_ADMIN"),
            "description": incoming_request.get("description", "") 
        }

        print(f"🔄 [Module 2] Assigned Trace ID: {orchestration_id}")
        print(f"🚀 [Module 2] Forwarding to Gatekeeper (Security Layer)...")

        # FEATURE: Fail-Safe Networking
        try:
            # Forward to Gatekeeper (Port 5000/5004)
            response = requests.post(GATEKEEPER_URL, json=standardized_payload, timeout=10)
            
            print(f"✅ [Module 2] Downstream Response: {response.status_code}")
            return jsonify(response.json()), response.status_code

        except requests.exceptions.ConnectionError:
            print("❌ [Module 2] ERROR: Gatekeeper is offline.")
            return jsonify({
                "final_status": "SYSTEM_ERROR",
                "risk_score": 0,
                "ui_message": "System Error: Gatekeeper (Security Module) is currently down."
            }), 503

    except Exception as e:
        print(f"❌ [Module 2] Internal Error: {e}")
        return jsonify({"error": "Orchestration Failed"}), 500

if __name__ == "__main__":
    # Orchestrator usually runs on Port 5001
    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    print(f"✅ Web Operating Layer initializing on Port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)