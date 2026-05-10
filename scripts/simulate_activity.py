import requests
import time
import json
import uuid
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

def simulate():
    # 1. Register a service
    service_name = f"payment-service-{uuid.uuid4().hex[:4]}"
    print(f"Registering {service_name}...")
    resp = requests.post(f"{BASE_URL}/services/register", json={
        "name": service_name,
        "environment": "production",
        "description": "Handles payment processing"
    })
    service_id = resp.json()["service_id"]
    api_key = resp.json()["api_key"]
    headers = {"X-API-KEY": api_key}

    # 2. Send 15 ERROR logs quickly (Triggers Anomaly Threshold > 10)
    print("Sending error spike (Threshold Trigger)...")
    for i in range(15):
        requests.post(f"{BASE_URL}/logs", headers=headers, json={
            "service_name": service_name,
            "message": f"Connection error #{i}: Failed to reach database at 10.0.0.5",
            "log_level": "ERROR",
            "timestamp": datetime.utcnow().isoformat()
        })
        time.sleep(0.1)

    print("Waiting 5s for anomaly detector to catch the spike...")
    time.sleep(5)

    # 3. Send a single CRITICAL log (Triggers Instant Incident)
    print("Sending CRITICAL log (Instant Trigger)...")
    requests.post(f"{BASE_URL}/logs", headers=headers, json={
        "service_name": service_name,
        "message": "CRITICAL: Kernel Panic - Out of Memory on core node. Service shutting down.",
        "log_level": "CRITICAL",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    print("Simulation complete. Check the dashboard!")

if __name__ == "__main__":
    simulate()
