import subprocess
import threading
import re
import time
import config

TUNNEL_URL = {"value": None}

def start_bore_tunnel():
    """Launches the bore tunnel pointing to the logging proxy port."""
    def run():
        cmd = ["bore", "local", str(config.LOGGING_PROXY_PORT), "--to", "bore.pub"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in proc.stdout:
            if "listening at bore.pub:" in line:
                match = re.search(r'bore\.pub:(\d+)', line)
                if match:
                    port = match.group(1)
                    url = f"http://bore.pub:{port}"
                    TUNNEL_URL["value"] = url
                    print("\n" + "=" * 70)
                    print("[Tunnel] SUCCESS: TUNNEL ESTABLISHED SUCCESSFULLY")
                    print(f"BASE URL FOR CLAUDE CODE: {url}")
                    print("=" * 70 + "\n")
                    print("Run the following PowerShell command on your PC to connect Claude Code:")
                    print(f'$env:ANTHROPIC_BASE_URL="{url}"')
                    print(f'$env:ANTHROPIC_AUTH_TOKEN="sk-anything"')
                    print(f'$env:ANTHROPIC_MODEL="{config.MODEL_NAME}"')
                    print('$env:MAX_THINKING_TOKENS=4000')
                    print('claude\n')
                    break

    t = threading.Thread(target=run, daemon=True)
    t.start()
    
    time.sleep(10)
    if not TUNNEL_URL["value"]:
        print("[Tunnel] WARNING: Tunnel URL was not established within 10s (bore.pub might be slow).")
    return TUNNEL_URL
