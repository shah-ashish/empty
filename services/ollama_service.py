import os
import subprocess
import sys
import time
import requests
import config

def start_ollama():
    """Starts Ollama background process with GPU visibility."""
    env = os.environ.copy()
    env.setdefault("CUDA_VISIBLE_DEVICES", "0,1")  # Auto-split across visible GPUs

    print(f"[Ollama] Starting Ollama server on port {config.OLLAMA_PORT}...")
    ollama_proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    # Health poll — Ollama can be slow on first boot
    for i in range(60):
        try:
            requests.get(config.OLLAMA_BASE_URL, timeout=5)
            print("[Ollama] SUCCESS: Ollama server is up and responsive.")
            return ollama_proc
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
            time.sleep(1)

    raise RuntimeError("[Ollama] FAILURE: Ollama did not respond within 60 seconds.")

def ensure_model_pulled():
    """Pulls the configured model using Ollama CLI with live progress output."""
    print(f"[Ollama] Pulling model '{config.MODEL_NAME}'...")
    proc = subprocess.Popen(
        ["ollama", "pull", config.MODEL_NAME],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for line in iter(proc.stdout.readline, ""):
        sys.stdout.write(f"\r{line.strip():<80}")
        sys.stdout.flush()

    proc.wait()
    print()  # newline after progress

    if proc.returncode == 0:
        print(f"[Ollama] SUCCESS: Successfully pulled model '{config.MODEL_NAME}'.")
    else:
        raise RuntimeError(f"[Ollama] FAILURE: Failed to pull model '{config.MODEL_NAME}'.")
