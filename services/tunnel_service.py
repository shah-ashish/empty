import subprocess
import re
import time
import config

TUNNEL_URL = {"value": None}

def start_ssh_tunnel():
    """Establishes a Pinggy reverse tunnel via SSH on port 443 (Kaggle-friendly).
    Uses log file + grep pattern (same proven approach as Local-Ai/cloudflared).
    """

    log_file = "/tmp/pinggy_tunnel.log"

    cmd = (
        f"ssh -p 443 "
        f"-o StrictHostKeyChecking=no "
        f"-o UserKnownHostsFile=/dev/null "
        f"-o ServerAliveInterval=30 "
        f"-o ServerAliveCountMax=6 "
        f"-R 0:localhost:{config.LOGGING_PROXY_PORT} "
        f"free.pinggy.io"
    )

    # Launch SSH tunnel in background, redirect all output to log file
    subprocess.Popen(
        f"nohup {cmd} > {log_file} 2>&1 &",
        shell=True,
    )

    print("[Tunnel] Waiting for Pinggy tunnel URL...")

    # Poll log file for the URL (same pattern as cloudflared in Local-Ai)
    for i in range(30):
        try:
            with open(log_file, "r") as f:
                content = f.read()
                # Match any https URL containing 'pinggy' in the domain
                matches = re.finditer(
                    r'(https://[a-zA-Z0-9\-]+\.(?:[a-zA-Z0-9\-]+\.)*pinggy[a-zA-Z0-9\-]*\.[a-z]+)',
                    content
                )
                for m in matches:
                    url = m.group(1)
                    if "dashboard.pinggy.io" not in url:
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
                        return TUNNEL_URL
        except FileNotFoundError:
            pass

        time.sleep(1)

    # If no URL found, dump the log for debugging
    print("[Tunnel] WARNING: Tunnel URL not found within 30s.")
    print("[Tunnel] Log file contents:")
    try:
        with open(log_file, "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("[Tunnel] Log file not created — SSH may have failed to start.")

    return TUNNEL_URL
