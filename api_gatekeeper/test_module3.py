import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:5003"

print("=" * 60)
print("STARTING MODULE 3 TEST (WITHOUT POSTMAN)")
print("=" * 60)

# -------------------------------------------------
# 1. Test HEALTH endpoint (GET)
# -------------------------------------------------
print("\n[1] Testing /health endpoint")

try:
    health_response = requests.get(f"{BASE_URL}/health")
    print("Status Code:", health_response.status_code)
    print("Response:", health_response.json())
except Exception as e:
    print("Health test failed:", e)

# -------------------------------------------------
# 2. Test INTERCEPT endpoint (POST)
# -------------------------------------------------
print("\n[2] Testing /intercept endpoint")

headers = {
    "Authorization": "EthicXHRSecret2026",
    "Content-Type": "application/json"
}

payload = {
    "actor_role": "HR",
    "action_type": "screening",
    "candidate_id": "C123",
    "context": "Initial screening",
    "timestamp": datetime.now().isoformat()
}

try:
    intercept_response = requests.post(
        f"{BASE_URL}/intercept",
        json=payload,
        headers=headers
    )
    print("Status Code:", intercept_response.status_code)
    print("Response:", intercept_response.json())
except Exception as e:
    print("Intercept test failed:", e)

print("\n" + "=" * 60)
print("MODULE 3 TEST COMPLETED")
print("=" * 60)
