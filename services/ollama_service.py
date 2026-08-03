import os
import subprocess
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
    """Pulls the configured model using Ollama CLI."""
    print(f"[Ollama] Pulling model '{config.MODEL_NAME}'...")
    cmd = ["ollama", "pull", config.MODEL_NAME]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"[Ollama] SUCCESS: Successfully pulled model '{config.MODEL_NAME}'.")
    else:
        raise RuntimeError(f"[Ollama] FAILURE: Failed to pull model '{config.MODEL_NAME}'.")
