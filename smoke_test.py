import requests
import json
import config

def run_smoke_test():
    """Runs a test request directly through the logging proxy (port 5000)."""
    print(f"[Test] Executing smoke test against {config.MODEL_NAME} via Proxy...")
    
    url = f"http://localhost:{config.LOGGING_PROXY_PORT}/v1/messages"
    headers = {
        "x-api-key": "sk-anything",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": config.MODEL_NAME,
        "max_tokens": 200,
        "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
        "tools": [{
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "City name"}},
                "required": ["location"],
            },
        }],
        "stream": True,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
        print("[Test] SUCCESS: Response Status Code:", resp.status_code)
        for line in resp.iter_lines():
            if line:
                print(line.decode())
    except Exception as e:
        print(f"[Test] FAILURE: Smoke test failed: {e}")

if __name__ == "__main__":
    run_smoke_test()
