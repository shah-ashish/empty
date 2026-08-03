from flask import Flask, request, Response
import requests
import json
import threading
from datetime import datetime
import config

app = Flask(__name__)

totals = {"input_tokens": 0, "output_tokens": 0, "requests": 0}
totals_lock = threading.Lock()

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(config.LOG_FILE, "a") as f:
        f.write(line + "\n")

def record_usage(input_tokens, output_tokens, stop_reason=None):
    with totals_lock:
        totals["input_tokens"] += input_tokens
        totals["output_tokens"] += output_tokens
        totals["requests"] += 1
        log(f"THIS REQUEST -- input: {input_tokens} | output: {output_tokens} | total: {input_tokens + output_tokens} | stop_reason: {stop_reason}")
        log(f"RUNNING TOTAL -- requests: {totals['requests']} | input: {totals['input_tokens']} | output: {totals['output_tokens']} | grand total: {totals['input_tokens'] + totals['output_tokens']}")

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    log("=" * 80)
    log(f"--> {request.method} /{path}")

    body = request.get_data()
    is_stream_request = False
    try:
        parsed = json.loads(body)
        is_stream_request = bool(parsed.get("stream"))
    except Exception:
        pass

    forwarded_headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    upstream = requests.request(
        method=request.method,
        url=f"{config.LITELLM_BASE_URL}/{path}",
        headers=forwarded_headers,
        data=body,
        params=request.args,
        stream=True,
        timeout=300,
    )

    def generate():
        input_tokens = output_tokens = 0
        stop_reason = None
        buffer = b""
        for chunk in upstream.iter_content(chunk_size=None):
            if not chunk:
                continue
            buffer += chunk
            yield chunk
            if is_stream_request:
                for raw_line in buffer.split(b"\n"):
                    line = raw_line.decode(errors="ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    try:
                        evt = json.loads(line[len("data:"):].strip())
                    except Exception:
                        continue
                    usage = evt.get("message", {}).get("usage") or evt.get("usage")
                    if usage:
                        input_tokens = usage.get("input_tokens", input_tokens)
                        output_tokens = usage.get("output_tokens", output_tokens)
                    delta = evt.get("delta", {})
                    if delta.get("stop_reason"):
                        stop_reason = delta["stop_reason"]
                buffer = b""
        if is_stream_request and (input_tokens or output_tokens):
            record_usage(input_tokens, output_tokens, stop_reason)
        elif not is_stream_request:
            try:
                data = json.loads(buffer)
                usage = data.get("usage", {})
                record_usage(usage.get("input_tokens", 0), usage.get("output_tokens", 0), data.get("stop_reason"))
            except Exception:
                pass

    return Response(generate(), status=upstream.status_code, content_type=upstream.headers.get("content-type"))

def start_logging_proxy():
    """Starts the Flask Proxy in a background thread."""
    def run():
        app.run(host="0.0.0.0", port=config.LOGGING_PROXY_PORT, threaded=True)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    print(f"[Proxy] SUCCESS: Logging proxy active on port {config.LOGGING_PROXY_PORT} -> forwarding to {config.LITELLM_BASE_URL}")
