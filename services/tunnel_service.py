import subprocess
import threading
import re
import time
import config

TUNNEL_URL = {"value": None}

def start_ssh_tunnel():
    """Establishes a Pinggy reverse tunnel via SSH on port 443 (Kaggle-friendly)."""

    cmd = [
        "ssh",
        "-p", "443",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=6",
        "-R", f"0:localhost:{config.LOGGING_PROXY_PORT}",
        "free.pinggy.io"
    ]

    def run():
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in proc.stdout:
            stripped = line.strip()
            if not stripped:
                continue

            # Pinggy prints both http and https URLs — capture the https one
            match = re.search(r'(https://[a-zA-Z0-9\-]+\.a\.pinggy\.(link|online))', stripped)
            if match and not TUNNEL_URL["value"]:
                url = match.group(1)
                TUNNEL_URL["value"] = url

                print("\n" + "=" * 70)
                print("[Tunnel] SUCCESS: PINGGY TUNNEL ESTABLISHED")
                print(f"BASE URL FOR CLAUDE CODE: {url}")
                print("=" * 70 + "\n")
                print("Run the following in PowerShell on your PC to connect Claude Code:")
                print(f'$env:ANTHROPIC_BASE_URL="{url}"')
                print(f'$env:ANTHROPIC_AUTH_TOKEN="sk-anything"')
                print(f'$env:ANTHROPIC_MODEL="{config.MODEL_NAME}"')
                print('$env:MAX_THINKING_TOKENS=4000')
                print('claude\n')

    t = threading.Thread(target=run, daemon=True)
    t.start()

    # Give Pinggy time to establish and print the URL
    time.sleep(12)

    if not TUNNEL_URL["value"]:
        print("[Tunnel] WARNING: Tunnel URL not received within 12s. Pinggy may be slow — check output above.")

    return TUNNEL_URL
