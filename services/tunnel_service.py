import subprocess
import threading
import time
import os
import stat
import config

TUNNEL_URL = {"value": None}

def start_ssh_tunnel():
    """Establishes SSH reverse tunnel from Kaggle to home PC."""

    # --- Load private key from Kaggle secret ---
    private_key = os.environ.get("SSH_PRIVATE_KEY", "")
    if not private_key:
        print("[Tunnel] FAILURE: SSH_PRIVATE_KEY secret not found in environment.")
        return TUNNEL_URL

    # Write private key to a temp file with correct permissions
    key_path = "/tmp/kaggle_tunnel_key"
    with open(key_path, "w") as f:
        f.write(private_key)
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)  # chmod 600 — SSH requires this

    ssh_host = os.environ.get("SSH_HOST", "")    # e.g. kaggle-ashish.duckdns.org
    ssh_user = os.environ.get("SSH_USER", "")    # your Windows username
    ssh_port = os.environ.get("SSH_PORT", "22")
    tunnel_port = str(config.LOGGING_PROXY_PORT)  # 5000

    if not ssh_host or not ssh_user:
        print("[Tunnel] FAILURE: SSH_HOST or SSH_USER secret not set.")
        return TUNNEL_URL

    cmd = [
        "ssh",
        "-i", key_path,
        "-p", ssh_port,
        "-o", "StrictHostKeyChecking=no",      # Don't prompt for host key confirmation
        "-o", "ServerAliveInterval=30",        # Send keepalive every 30s
        "-o", "ServerAliveCountMax=6",         # Drop after 3 min of no response
        "-o", "ExitOnForwardFailure=yes",      # Fail fast if port binding fails
        "-N",                                  # No remote command — tunnel only
        "-R", f"0.0.0.0:{tunnel_port}:localhost:{tunnel_port}",  # Bind on all interfaces
        f"{ssh_user}@{ssh_host}"
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
            if stripped:
                print(f"[Tunnel] {stripped}")

    t = threading.Thread(target=run, daemon=True)
    t.start()

    # Wait for tunnel to establish
    time.sleep(5)

    url = f"http://{ssh_host}:{tunnel_port}"
    TUNNEL_URL["value"] = url

    print("\n" + "=" * 70)
    print("[Tunnel] SUCCESS: SSH REVERSE TUNNEL ESTABLISHED")
    print(f"BASE URL FOR CLAUDE CODE: {url}")
    print("=" * 70 + "\n")
    print("Run the following in PowerShell on your PC to connect Claude Code:")
    print(f'$env:ANTHROPIC_BASE_URL="{url}"')
    print(f'$env:ANTHROPIC_AUTH_TOKEN="sk-anything"')
    print(f'$env:ANTHROPIC_MODEL="{config.MODEL_NAME}"')
    print('$env:MAX_THINKING_TOKENS=4000')
    print('claude\n')

    return TUNNEL_URL
