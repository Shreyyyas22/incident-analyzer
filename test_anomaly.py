import json
import urllib.request
import uuid
import time

def test():
    name = f"anomaly-test-{uuid.uuid4()}"
    req = urllib.request.Request("http://localhost:8000/services/register", data=json.dumps({"name":name, "environment":"dev"}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read())
        api_key = res["api_key"]
        service_id = res["service_id"]
        print(f"Registered service: {name} ({service_id})")

    print("Spamming 15 errors...")
    from datetime import datetime, timezone
    for i in range(15):
        now = datetime.now(timezone.utc).isoformat()
        log_data = json.dumps({
            "service_name": name,
            "log_level": "ERROR",
            "message": f"Error {i}",
            "timestamp": now
        }).encode()
        req = urllib.request.Request("http://localhost:8000/logs", data=log_data, headers={'Content-Type': 'application/json', 'X-API-Key': api_key})
        with urllib.request.urlopen(req) as response:
            pass

    print("Logs sent. Waiting 35 seconds for Celery Beat to trigger...")
    time.sleep(35)

    req = urllib.request.Request("http://localhost:8000/incidents")
    with urllib.request.urlopen(req) as response:
        incidents = json.loads(response.read())
        print(f"Total incidents: {len(incidents)}")
        for inc in incidents:
            if inc["service_id"] == service_id:
                print("FOUND INCIDENT:", inc)
                return

    print("FAILED: Incident not found!")

if __name__ == "__main__":
    test()
