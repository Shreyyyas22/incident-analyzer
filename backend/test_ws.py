import asyncio
import websockets
import json
import urllib.request
import uuid

async def test_ws():
    name = f"ws-test-{uuid.uuid4()}"
    req = urllib.request.Request("http://localhost:8000/services/register", data=json.dumps({"name":name, "environment":"dev"}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read())
        api_key = res["api_key"]

    async with websockets.connect('ws://localhost:8000/ws/logs') as websocket:
        print("Connected to WS")
        
        log_data = json.dumps({
            "service_name": name,
            "log_level": "WARNING",
            "message": "This is a real-time test log",
            "timestamp": "2026-05-10T10:05:00Z"
        }).encode()
        
        req = urllib.request.Request("http://localhost:8000/logs", data=log_data, headers={'Content-Type': 'application/json', 'X-API-Key': api_key})
        with urllib.request.urlopen(req) as response:
            print("Log sent, response:", response.status)

        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        print("Received from WS:", message)

asyncio.run(test_ws())
