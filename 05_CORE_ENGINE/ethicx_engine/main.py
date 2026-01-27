import os
import sys
import requests
import spacy
from flask import Flask, request, jsonify
from spacy.matcher import PhraseMatcher

app = Flask(__name__)

# --- CONFIGURATION ---
ENFORCER_URL = "http://127.0.0.1:5003/enforce"

# --- NLP SETUP ---
print("⏳ [Module 5A] Initializing Complete NLP Brain...")
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("❌ Error: Run 'python -m spacy download en_core_web_sm'")
    sys.exit(1)

# --- 1. FULL KNOWLEDGE BASE ---
JOB_PROFILES = {
    "avionics_software_engineer": {
        "platinum": ['do-178c', 'embedded c', 'ada', 'spark ada', 'misra', 'safe coding'],
        "gold": ['vxworks', 'green hills', 'rtos', 'multithreading', 'isr'],
        "silver": ['python', 'c++', 'linux', 'git', 'jira'],
        "bias": ['rockstar', 'ninja', 'young', 'energetic']
    },
    "verification_engineer": {
        "platinum": ['verification', 'validation', 'mc/dc', 'structural coverage'],
        "gold": ['vectorcast', 'ldra', 'rtrt', 'test cases'],
        "silver": ['python scripting', 'jenkins', 'automation'],
        "bias": ['perfectionist', 'obsessive']
    },
    "systems_architect": {
        "platinum": ['arp4754', 'system requirements', 'doors', 'cameo'],
        "gold": ['ima', 'arinc 653', 'sysml', 'icd'],
        "silver": ['matlab', 'simulink', 'visio'],
        "bias": ['visionary', 'guru']
    },
    "safety_engineer": {
        "platinum": ['arp4761', 'fmea', 'fta', 'ssa', 'pssa'],
        "gold": ['reliability', 'hazard analysis', 'mil-std-882'],
        "silver": ['excel', 'cafta'],
        "bias": ['pessimist', 'paranoid']
    }
    # (Remaining roles follow this pattern)
}

# --- 2. ADVANCED NLP HELPERS ---
def is_negated(token):
    """Checks if a skill is mentioned as LACKING (e.g., 'No DO-178C experience')"""
    for child in token.children:
        if child.dep_ == "neg" or child.text.lower() in ["no", "not", "lack", "without"]:
            return True
    return False

def get_profile(role_name):
    role_lower = str(role_name).lower()
    if any(x in role_lower for x in ["test", "verify", "v&v"]):
        return JOB_PROFILES["verification_engineer"], "V&V Engineer"
    elif "architect" in role_lower or "system" in role_lower:
        return JOB_PROFILES["systems_architect"], "Systems Architect"
    return JOB_PROFILES["avionics_software_engineer"], "Avionics Software Engineer"

# --- 3. MAIN API ENDPOINT ---
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    user_role = data.get('role', 'Avionics')
    profile, mode_name = get_profile(user_role)
    
    # Process text
    raw_text = (str(data.get('description', '')) + " " + str(user_role)).lower()
    doc = nlp(raw_text)
    matcher = PhraseMatcher(nlp.vocab)
    
    # Setup matcher
    for category in ["platinum", "gold", "silver", "bias"]:
        patterns = [nlp.make_doc(text) for text in profile.get(category, [])]
        matcher.add(category.upper(), patterns)

    matches = matcher(doc)
    score, factors, reasons, processed = 50, [], [], set()

    # Score calculation
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span = doc[start:end]
        if span.text in processed: continue
        
        # Check for negation
        if is_negated(span.root):
            reasons.append(f"Skipped negated: {span.text}")
            continue

        processed.add(span.text)
        if label == "PLATINUM": score -= 15; factors.append(f"{span.text} (Critical)")
        elif label == "GOLD": score -= 10; factors.append(f"{span.text} (High)")
        elif label == "SILVER": score -= 5; factors.append(f"{span.text} (Bonus)")
        elif label == "BIAS": score += 40; reasons.append(f"Bias Found: {span.text}")

    # Final Result
    payload = {
        "risk_score": max(0, min(100, score)),
        "positive_factors": factors,
        "reason": "; ".join(reasons),
        "original_data": data
    }

    # Communication with Enforcer
    try:
        res = requests.post(ENFORCER_URL, json=payload, timeout=5)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": f"Enforcer connection failed: {e}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 5002))
    app.run(host="0.0.0.0", port=port)