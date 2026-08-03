import os

# ==============================================================================
# SINGLE SOURCE OF TRUTH FOR MODEL NAME & CONFIG
# ==============================================================================
MODEL_NAME = "qwen2.5-coder:7b"  # Change model here

# Port Configurations
OLLAMA_PORT = 11434
LITELLM_PORT = 4000
LOGGING_PROXY_PORT = 5000

# Base URLs
OLLAMA_BASE_URL = f"http://localhost:{OLLAMA_PORT}"
LITELLM_BASE_URL = f"http://localhost:{LITELLM_PORT}"

# LiteLLM Proxy Tuning
NUM_CTX = 16384
TEMPERATURE = 0.3
REPEAT_PENALTY = 1.15
THINK = True

# Logging Configuration
LOG_FILE = "claude_requests.log"
