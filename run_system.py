import subprocess
import time
import sys
import os

# --- BASE DIRECTORY ---
# This ensures we always find the folders correctly on Windows
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CONFIGURATION: Define your 6 Tiers ---
# Updated to match your specific nested folder structure
SERVICES = [
    {
        "name": "TIER 6: Audit Logger",    
        "path": "06_INFRASTRUCTURE/audit_logger/audit_logger.py", 
        "port": 5005
    },
    {
        "name": "TIER 5B: Enforcer",      
        "path": "05_CORE_ENGINE/decision_enforcer/app.py", 
        "port": 5003
    },
    {
        "name": "TIER 5A: EthicX Engine", 
        "path": "05_CORE_ENGINE/ethicx_engine/main.py", 
        "port": 5002
    },
    {
        "name": "TIER 3: Gatekeeper",     
        "path": "03_API_GATEWAY/api_gatekeeper/app.py", 
        "port": 5004
    },
    {
        "name": "TIER 2: Web Operating",  
        "path": "02_WEB_LAYER/web_operating_layer/app.py", 
        "port": 5001
    },
    {
        "name": "TIER 1: User Interface", 
        "path": "01_USER_INTERFACE/hr_ui/app.py", 
        "port": 8000
    },
]

processes = []

def launch_services():
    print("🚀 Starting EthicX-HR 6-Tier Microservice Ecosystem...")
    print("-" * 65)

    for service in SERVICES:
        # Construct the Absolute Path using Windows separators
        full_path = os.path.join(BASE_DIR, service['path'].replace('/', os.sep))
        
        if not os.path.exists(full_path):
            print(f"❌ ERROR: File not found at: {full_path}")
            print(f"   Please check if the folder or filename is spelled correctly.\n")
            continue

        print(f"⏳ Launching {service['name']} on Port {service['port']}...")
        
        # Start the process using the current Python interpreter
        process = subprocess.Popen(
            [sys.executable, full_path],
            env={**os.environ, "FLASK_RUN_PORT": str(service['port'])},
            stdout=None, 
            stderr=None
        )
        processes.append(process)
        # Give each service 2 seconds to bind to the port
        time.sleep(2)

    print("-" * 65)
    print("✅ SYSTEM CHECK COMPLETE")
    print("🔗 DASHBOARD: http://127.0.0.1:8000")
    print("🛑 PRESS CTRL+C TO TERMINATE ALL SERVICES")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down microservices...")
        for p in processes:
            p.terminate()
        print("✅ All processes killed. System offline.")

if __name__ == "__main__":
    launch_services()