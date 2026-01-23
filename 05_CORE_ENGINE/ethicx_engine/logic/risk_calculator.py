# Function to calculate final score
class RiskCalculator:
    @staticmethod
    def calculate_verdict(policy_score, bias_score, policy_issues, bias_issues):
        total_score = policy_score + bias_score
        decision = "ALLOW"
        explanation = "Action complies with ethical standards."

        all_issues = policy_issues + bias_issues

        # LOGIC THRESHOLDS
        if total_score >= 60:
            decision = "RESTRICT"
            explanation = f"High Ethical Risk Detected ({total_score}/100). Issues: {'; '.join(all_issues)}"
        elif total_score >= 20:
            decision = "FLAG"
            explanation = f"Potential Risk Detected ({total_score}/100). Review required: {'; '.join(all_issues)}"
        
        return {
            "decision": decision,
            "risk_score": total_score,
            "reason": explanation
        }