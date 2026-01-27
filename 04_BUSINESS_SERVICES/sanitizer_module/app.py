import os
import sys
from flask import Flask, request, jsonify

# Add current directory to path so we can import cleaner.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cleaner import ResumeCleaner

app = Flask(__name__)
scrubber = ResumeCleaner()

@app.route('/')
def home():
    return jsonify({"module": "04B_SANITIZER", "status": "Ready"})

@app.route('/sanitize', methods=['POST'])
def handle_sanitization():
    data = request.get_json()
    
    if not data or 'description' not in data:
        return jsonify({"error": "No description field found to sanitize"}), 400

    print(f"🧼 [4B] Scrubbing resume for Role: {data.get('role', 'Unknown')}")
    
    # Use the cleaner logic
    raw_text = data.get('description', '')
    clean_text = scrubber.full_sanitize(raw_text)

    # Prepare the sanitized package for return
    # This structure is designed to be accepted by Module 05A (AI Engine)
    sanitized_payload = {
        "candidate_id": data.get('candidate_id'),
        "role": data.get('role'),
        "description": clean_text,
        "initial_score": data.get('initial_score')
    }

    return jsonify({
        "status": "Success",
        "sanitized_data": sanitized_payload
    }), 200

if __name__ == '__main__':
    # Dynamically pick up port 5002 from run_system.py
    port = int(os.environ.get("FLASK_RUN_PORT", 5002))
    print(f"🧼 Sanitizer Microservice active on Port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)