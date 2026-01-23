import subprocess
import time
import os
import sys
import signal

# Define your microservices configuration
SERVICES = [
    {
        "name": "API Gateway",
        "path": "03_API_GATEWAY/api_gatekeeper/app.py",
        "port": 5000
    },
    {
        "name": "Applicant Service",
        "path": "04_BUSINESS_SERVICES/applicant_service/app.py",
        "port": 5001
    },
    {
        "name": "Sanitizer Module",
        "path": "04_BUSINESS_SERVICES/sanitizer_module/app.py",
        "port": 5002
    },
    {
        "name": "HR Backend",
        "path": "04_BUSINESS_SERVICES/ethicx_hr/app.py",
        "port": 5003
    }
]

processes = []

def start_service(service):
    print(f"🚀 Starting {service['name']} on Port {service['port']}...")
    cmd = [sys.executable, service['path']]
    try:
        folder = os.path.dirname(service['path'])
        script = os.path.basename(service['path'])
        
        p = subprocess.Popen(
            [sys.executable, script], 
            cwd=folder,
            env=dict(os.environ, FLASK_RUN_PORT=str(service['port']))
        )
        processes.append(p)
        print(f"✅ {service['name']} is running (PID: {p.pid})")
    except Exception as e:
        print(f"❌ Failed to start {service['name']}: {e}")

def stop_all_services(signum, frame):
    print("\n\n🛑 Shutting down EthicX-HR System...")
    for p in processes:
        p.terminate()
    print("All services stopped. Goodbye!")
    sys.exit(0)

if __name__ == "__main__":
    print("="*40)
    print("      ETHICX-HR MICROSERVICES LAUNCHER      ")
    print("="*40)

    signal.signal(signal.SIGINT, stop_all_services)

    for service in SERVICES:
        start_service(service)
        time.sleep(2)

    while True:
        time.sleep(1)