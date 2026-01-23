# api_gatekeeper/validators/inspector.py
import re

def inspect_payload(data):
    """
    Scans input for security risks (PII leaks).
    Returns: (is_safe, data, error_message)
    """
    text = data.get("description", "") or str(data)

    # 1. Check for Phone Numbers
    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    if phone_pattern.search(text):
        return False, None, "Security Alert: PII (Phone Number) detected."

    # 2. Check for Email Addresses
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    if email_pattern.search(text):
        return False, None, "Security Alert: PII (Email Address) detected."

    return True, data, None