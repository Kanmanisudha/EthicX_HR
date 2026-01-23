import time
import uuid
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
# Connects to Module 3 (Gatekeeper) on Port 5004
GATEKEEPER_URL = "http://127.0.0.1:5004/intercept"

@app.route("/")
def home():
    return "EthicX-HR Web Operating Layer (Module 2) is running on Port 5001"

@app.route("/orchestrate/screening", methods=["POST"])
def orchestrate_screening():
    try:
        # FEATURE 1: Input Validation
        # We grab the raw data from the UI
        incoming_request = request.json
        print(f"\n📥 [Module 2] Received Request for Candidate ID: {incoming_request.get('candidate_id')}")

        # FEATURE 2: Legal Audit Trail
        # We generate a unique ID (UUID) for this specific transaction.
        # This allows us to track this specific resume's journey forever.
        orchestration_id = str(uuid.uuid4())
        
        # FEATURE 3: Data Standardization
        # We create a new, clean packet of data. We don't just blindly forward 
        # what the UI sent. We structure it strictly.
        standardized_payload = {
            "orchestration_id": orchestration_id,
            "timestamp": datetime.utcnow().isoformat(), # Adds precise timing
            "origin": "HR_UI",
            "candidate_id": incoming_request.get("candidate_id"),
            "action_type": incoming_request.get("action"),
            "requested_by": incoming_request.get("requested_by"),
            "description": incoming_request.get("description", "") 
        }

        print(f"🔄 [Module 2] Assigned ID: {orchestration_id}")
        print(f"🚀 [Module 2] Forwarding to Gatekeeper (Port 5004)...")

        # FEATURE 4: Fail-Safe Networking
        # We try to talk to the Gatekeeper. If it fails, we catch it.
        try:
            response = requests.post(GATEKEEPER_URL, json=standardized_payload)
            
            # FEATURE 5: Transparent Pass-Through
            # We return the EXACT response from the AI (including risk scores)
            # so the UI gets the full picture.
            print(f"✅ [Module 2] Received Response from Gatekeeper: {response.status_code}")
            return jsonify(response.json()), response.status_code

        except requests.exceptions.ConnectionError:
            # FEATURE 6: Graceful Failure
            # If the backend is dead, we tell the UI politely instead of crashing.
            print("❌ [Module 2] ERROR: Connection Refused. Is Module 3 (Port 5004) running?")
            return jsonify({
                "decision": "ERROR",
                "risk_score": 0,
                "reason": "System Error: Gatekeeper (Security Module 3) is down."
            }), 503

    except Exception as e:
        print(f"❌ [Module 2] Internal Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("✅ Web Operating Layer running on Port 5001")
    app.run(host="127.0.0.1", port=5001, debug=True)