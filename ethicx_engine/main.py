import requests
import spacy
from spacy.matcher import PhraseMatcher
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
ENFORCER_URL = "http://127.0.0.1:5003/enforce"

# --- LOAD NLP MODEL ---
print("⏳ [Module 4] Loading NLP Brain...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ [Module 4] NLP Model Loaded Successfully.")
except OSError:
    print("❌ [Module 4] Error: Spacy model not found.")
    print("   Please run: python -m spacy download en_core_web_sm")
    exit(1)

@app.route('/')
def home():
    return jsonify({"status": "Online", "module": "Module 4 (Dynamic NLP Engine)", "port": 5002})

# --- 1. DYNAMIC KNOWLEDGE BASE (10 ROLES) ---
JOB_PROFILES = {
    # 1. CORE DEVELOPER
    "avionics_software_engineer": {
        "platinum": ['do-178c', 'embedded c', 'ada', 'spark ada', 'misra', 'safe coding'],
        "gold": ['vxworks', 'green hills', 'rtos', 'multithreading', 'interrupt service routines', 'isr'],
        "silver": ['python', 'c++', 'linux', 'git', 'jira', 'bitbucket'],
        "bias": ['rockstar', 'ninja', '10x engineer', 'young', 'energetic']
    },
    # 2. TESTER (V&V)
    "verification_engineer": {
        "platinum": ['verification', 'validation', 'structural coverage', 'mc/dc', 'statement coverage'],
        "gold": ['vectorcast', 'ldra', 'rtrt', 'parasoft', 'test cases', 'regression testing'],
        "silver": ['python scripting', 'jenkins', 'automation', 'selenium'],
        "bias": ['perfectionist', 'obsessive', 'native english']
    },
    # 3. SYSTEMS ARCHITECT
    "systems_architect": {
        "platinum": ['arp4754', 'system requirements', 'traceability', 'doors', 'cameo'],
        "gold": ['ima', 'integrated modular avionics', 'arinc 653', 'sysml', 'interface control document'],
        "silver": ['matlab', 'simulink', 'visio', 'agile'],
        "bias": ['visionary', 'guru', 'culture fit']
    },
    # 4. CERTIFICATION / DER
    "certification_engineer": {
        "platinum": ['certification', 'der', 'faa', 'easa', 'audit', 'soi', 'stage of involvement'],
        "gold": ['psac', 'sas', 'compliance', 'airworthiness'],
        "silver": ['technical writing', 'negotiation', 'project management'],
        "bias": ['policeman', 'bureaucrat']
    },
    # 5. SAFETY ENGINEER
    "safety_engineer": {
        "platinum": ['arp4761', 'fmea', 'fault tree analysis', 'fta', 'ssa', 'pssa'],
        "gold": ['reliability', 'common cause failure', 'hazard analysis', 'mil-std-882'],
        "silver": ['excel', 'cafta', 'isograph'],
        "bias": ['pessimist', 'paranoid']
    },
    # 6. MODEL BASED DESIGN (MBD)
    "mbd_engineer": {
        "platinum": ['do-331', 'scade', 'simulink', 'stateflow', 'model based design'],
        "gold": ['auto-coding', 'kcg', 'embedded coder', 'control laws', 'pid'],
        "silver": ['matlab script', 'c', 'simulation'],
        "bias": ['artist', 'visual thinker']
    },
    # 7. RTOS SPECIALIST
    "rtos_specialist": {
        "platinum": ['bsp', 'board support package', 'device drivers', 'interrupt latency'],
        "gold": ['memory management', 'mmu', 'context switching', 'arinc 653', 'partitioning'],
        "silver": ['assembly', 'jtag', 'oscilloscope'],
        "bias": ['wizard', 'deep diver']
    },
    # 8. CONFIGURATION MANAGEMENT
    "cm_engineer": {
        "platinum": ['configuration management', 'version control', 'change control board', 'ccb'],
        "gold": ['git', 'svn', 'clearcase', 'synergy', 'bamboo', 'jenkins'],
        "silver": ['scripting', 'bash', 'powershell', 'devops'],
        "bias": ['gatekeeper', 'controller']
    },
    # 9. TOOL QUALIFICATION
    "tool_qual_engineer": {
        "platinum": ['do-330', 'tool qualification', 'tql', 'tool operational requirements'],
        "gold": ['verification tool', 'development tool', 'qualification plan'],
        "silver": ['validation', 'scripting', 'qa'],
        "bias": ['nitpicker']
    },
    # 10. CYBERSECURITY
    "cybersecurity_engineer": {
        "platinum": ['do-326a', 'ed-202a', 'airworthiness security', 'threat analysis'],
        "gold": ['security risk assessment', 'penetration testing', 'pki', 'encryption'],
        "silver": ['linux', 'network security', 'firewalls'],
        "bias": ['hacker', 'black hat']
    }
}

# --- HELPER: CONTEXT SWITCHER ---
def get_profile_for_role(role_name):
    """
    Intelligently maps the user's input string (e.g., "Sr. V&V Eng") to a known Profile Key.
    """
    role_lower = str(role_name).lower()

    if "test" in role_lower or "verification" in role_lower or "validation" in role_lower or "v&v" in role_lower:
        return JOB_PROFILES["verification_engineer"], "V&V Engineer"
    elif "architect" in role_lower or "system" in role_lower:
        return JOB_PROFILES["systems_architect"], "Systems Architect"
    elif "cert" in role_lower or "compliance" in role_lower or "der" in role_lower:
        return JOB_PROFILES["certification_engineer"], "Certification Engineer"
    elif "safety" in role_lower or "reliability" in role_lower:
        return JOB_PROFILES["safety_engineer"], "Safety Engineer"
    elif "model" in role_lower or "simulink" in role_lower or "scade" in role_lower:
        return JOB_PROFILES["mbd_engineer"], "MBD Engineer"
    elif "rtos" in role_lower or "kernel" in role_lower or "bsp" in role_lower:
        return JOB_PROFILES["rtos_specialist"], "RTOS Specialist"
    elif "config" in role_lower or "release" in role_lower or "cm" in role_lower:
        return JOB_PROFILES["cm_engineer"], "CM Engineer"
    elif "tool" in role_lower or "qual" in role_lower:
        return JOB_PROFILES["tool_qual_engineer"], "Tool Qual Engineer"
    elif "security" in role_lower or "cyber" in role_lower:
        return JOB_PROFILES["cybersecurity_engineer"], "Cybersecurity Engineer"
    else:
        # Default fallback
        return JOB_PROFILES["avionics_software_engineer"], "Avionics Software Engineer"

def is_negated(token):
    """Checks if a skill is negated (e.g., 'No experience in DO-178C')"""
    for child in token.children:
        if child.dep_ == "neg" or child.text.lower() in ["no", "not", "lack", "without", "zero"]:
            return True
    if token.head.dep_ == "ROOT" or token.head.pos_ == "VERB":
        for child in token.head.children:
            if child.dep_ == "neg": return True
    return False

@app.route('/analyze', methods=['POST'])
def analyze_risk():
    data = request.json
    
    # 1. IDENTIFY ROLE & SELECT PROFILE
    user_role = data.get('role', 'Avionics') 
    profile_data, detected_mode = get_profile_for_role(user_role)
    
    print(f"\n✈️ [Module 4] Analysis Started | Input Role: '{user_role}'")
    print(f"   ⚙️  Active Profile: {detected_mode}")

    # 2. PREPARE TEXT
    raw_text = (str(data.get('description', '')) + " " + str(data.get('role', ''))).lower()
    doc = nlp(raw_text)

    # 3. BUILD MATCHER DYNAMICALLY FOR SELECTED PROFILE
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("PLATINUM", [nlp(text) for text in profile_data["platinum"]])
    matcher.add("GOLD", [nlp(text) for text in profile_data["gold"]])
    matcher.add("SILVER", [nlp(text) for text in profile_data["silver"]])
    matcher.add("BIAS", [nlp(text) for text in profile_data["bias"]])

    # 4. SCORING LOGIC
    matches = matcher(doc)
    score = 50 
    reasons = []
    positive_factors = []
    processed_keywords = set()

    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        root_token = span.root
        keyword_str = span.text

        if keyword_str in processed_keywords: continue
        
        # Check Negation
        if is_negated(root_token):
            print(f"   ⚠️ Negation Detected: '{keyword_str}' ignored.")
            reasons.append(f"Ignored negated skill: {keyword_str}")
            processed_keywords.add(keyword_str)
            continue

        processed_keywords.add(keyword_str)
        
        # Apply Weights
        if rule_id == "PLATINUM":
            score -= 15
            positive_factors.append(f"{keyword_str} (Critical)")
        elif rule_id == "GOLD":
            score -= 10
            positive_factors.append(f"{keyword_str} (High Value)")
        elif rule_id == "SILVER":
            score -= 5
            positive_factors.append(f"{keyword_str} (Bonus)")
        elif rule_id == "BIAS":
            score += 40
            reasons.append(f"Bias Detected: {keyword_str}")

    # 5. DOMAIN RELEVANCE CHECK
    final_decision = "ALLOW"
    if len(positive_factors) == 0:
        score = 100
        final_decision = "BLOCKED"
        reasons.append(f"❌ MISMATCH: No relevant skills found for {detected_mode}.")
    else:
        score = max(0, min(100, score))
        if score < 20:
            final_decision = "APPROVED"
            reasons.append(f"✅ STAR CANDIDATE: Strong {detected_mode} match.")
        elif score > 80:
            final_decision = "BLOCKED"
            reasons.append("❌ HIGH RISK: Bias or weak skills.")
        else:
            final_decision = "REVIEW"

    # 6. OUTPUT
    payload = {
        "decision": final_decision,
        "risk_score": score,
        "reason": "; ".join(reasons),
        "positive_factors": positive_factors,
        "original_data": data 
    }

    print(f"   [Score] {score}/100 | [Verdict] {final_decision}")
    
    try:
        response = requests.post(ENFORCER_URL, json=payload)
        return jsonify(response.json())
    except Exception as e:
        print(f"❌ Error contacting Enforcer: {e}")
        return jsonify({"error": "Enforcer Offline"}), 500

if __name__ == '__main__':
    print("✈️ Dynamic AI Engine running on Port 5002")
    app.run(host="127.0.0.1", port=5002, debug=True)