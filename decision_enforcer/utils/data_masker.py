# Logic to hide sensitive infodef mask_sensitive_data(data):
def mask_sensitive_data(data):
    """
    Hides PII (Personally Identifiable Information) to reduce bias.
    """
    sanitized = data.copy()
    
    # 1. Mask Name (e.g., "John Doe" -> "J*** D***")
    if "name" in sanitized:
        parts = sanitized["name"].split()
        masked_parts = [p[0] + "***" for p in parts]
        sanitized["name"] = " ".join(masked_parts)
    
    # 2. Mask Phone/Email (Simple redaction)
    if "phone" in sanitized:
        sanitized["phone"] = "[REDACTED]"
    if "email" in sanitized:
        sanitized["email"] = "[REDACTED]"
        
    return sanitized