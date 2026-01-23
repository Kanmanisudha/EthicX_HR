# NLP Function to scan text
from textblob import TextBlob

class BiasDetector:
    def __init__(self):
        # In a real ML model, you would load a trained file here.
        # For this prototype, we use dictionary lookups + Sentiment Analysis.
        pass

    def analyze_text(self, text, blocked_keywords):
        """
        Scans text for:
        1. Specific biased keywords (from rules.json)
        2. High subjectivity (opinion over fact)
        """
        issues = []
        score = 0
        blob = TextBlob(text.lower())

        # 1. Keyword Scanning
        for category, words in blocked_keywords.items():
            for word in words:
                if word in text.lower():
                    issues.append(f"Detected potential {category}: '{word}'")
                    score += 20  # Add risk points

        # 2. NLP Subjectivity Check (0.0 = Objective/Fact, 1.0 = Subjective/Opinion)
        # HR notes should be factual. High subjectivity is suspicious.
        if blob.sentiment.subjectivity > 0.7:
            issues.append("Language is highly subjective/emotional (Risk of unconscious bias).")
            score += 15

        # 3. Sentiment Check (Too negative without structure is risky)
        if blob.sentiment.polarity < -0.5:
            issues.append("Language is overly negative/hostile.")
            score += 10

        return {"score": score, "issues": issues}