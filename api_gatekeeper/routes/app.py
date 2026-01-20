import requests
from flask import Blueprint, request, jsonify
from datetime import datetime
from validators.inspector import inspect_payload

gatekeeper_bp = Blueprint('gatekeeper', __name__)

# CONFIG: Connects to Module 4 (AI Engine)
AI_ENGINE_URL = "http://127.0.0.1:5002/analyze"
response = requests.post(AI_ENGINE_URL, json=incoming_request) # <--- This sends the data

@gatekeeper_bp.route('/intercept', methods=['POST'])
def intercept():
    """
    1. Intercepts request from Orchestrator
    2. Checks for PII (Security)
    3. Forwards to AI Engine (Module 4) if safe
    """
    incoming_request = request.json
    
    print(f"🛡️ [Gatekeeper] Intercepted request.")

    # --- STEP 1: SECURITY CHECK (The Guard) ---
    is_safe, _, error_msg = inspect_payload(incoming_request)
    
    if not is_safe:
        print(f"⛔ [Gatekeeper] BLOCKED: {error_msg}")
        return jsonify({
            "status": "BLOCKED", 
            "decision": "BLOCKED", # <--- CRITICAL: UI needs this key to show Red Alert
            "reason": error_msg,
            "risk_score": 100
        })

    # --- STEP 2: FORWARD TO MODULE 4 (AI ENGINE) ---
    try:
        print(f"✅ [Gatekeeper] Data Safe. Forwarding to AI (Port 5002)...")
        
        response = requests.post(
            AI_ENGINE_URL,
            json=incoming_request, # Send the actual data the AI needs
            timeout=5
        )
        return jsonify(response.json())

    except requests.exceptions.ConnectionError:
        print("❌ [Gatekeeper] Error: AI Engine is Offline.")
        return jsonify({
            "status": "ERROR", 
            "message": "Gatekeeper could not reach AI Engine (Module 4)"
        }), 500