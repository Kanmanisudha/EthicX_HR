# Function to check rules.json
import json
import os

class PolicyChecker:
    def __init__(self, rules_path='policies/rules.json'):
        # Load rules from JSON file
        base_path = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(base_path, rules_path)
        
        with open(full_path, 'r') as f:
            self.rules = json.load(f)

    def check_rules(self, action_context):
        """
        Checks hard rules.
        Input: {"action": "Screening", "attributes_used": ["age", "experience"]}
        """
        violations = []
        risk_score = 0
        
        # Rule 1: Check for Protected Attributes usage
        used_attrs = action_context.get("attributes_used", [])
        for attr in used_attrs:
            if attr.lower() in self.rules["protected_attributes"]:
                violations.append(f"Illegal use of protected attribute: '{attr}'")
                risk_score += 50 # High penalty for legal violations

        return {
            "score": risk_score, 
            "violations": violations,
            "blocked_keywords": self.rules["blocked_keywords"] # Pass these to Bias Detector
        }