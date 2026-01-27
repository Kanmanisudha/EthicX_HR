import re

class ResumeCleaner:
    """
    Nature: Encapsulates all text-scrubbing logic to ensure 
    the AI Engine receives standardized, noise-free data.
    """
    
    @staticmethod
    def remove_html(text):
        # Strip out any HTML tags that might be in the parsed PDF/text
        return re.sub(r'<.*?>', '', text)

    @staticmethod
    def remove_special_chars(text):
        # Keep letters, numbers, and basic resume punctuation (.,-/), remove symbols
        return re.sub(r'[^a-zA-Z0-9\s.,\-\/]', '', text)

    @staticmethod
    def normalize_whitespace(text):
        # Remove tabs, newlines, and double spaces
        return " ".join(text.split())

    def full_sanitize(self, text):
        if not text:
            return ""
        text = self.remove_html(text)
        text = self.remove_special_chars(text)
        text = self.normalize_whitespace(text)
        return text