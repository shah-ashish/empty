#!/usr/bin/env bash

set -e

# Configurable GitHub Repository URL
REPO_URL="${REPO_URL:-https://github.com/shah-ashish/empty.git}"
REPO_DIR="$(basename -s .git "$REPO_URL")"
# 0. Clone repository if project files are not in current directory
if [ ! -f "main.py" ]; then
  if [ -d "$REPO_DIR" ]; then
    echo "- Found existing project folder '$REPO_DIR'. Entering directory..."
    cd "$REPO_DIR"
  else
    echo "- Cloning repository from $REPO_URL..."
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
  fi
fi

# Pull latest code updates if git repo exists
if [ -d ".git" ]; then
  echo "- Checking for latest updates..."
  git pull origin main 2>/dev/null || true
fi





echo "=========================================="
echo " Starting Kaggle Local LLM Proxy Pipeline"
echo "=========================================="

echo "=== Step 1: Checking / Creating Virtual Environment ==="
VENV_ACTIVE=0

# Detect Kaggle or any environment where ensurepip is disabled (venv won't work)
if python3 -c "import ensurepip" 2>/dev/null; then
    # ensurepip is available — safe to create a venv
    if [ ! -d "venv" ]; then
        echo "[VENV] Virtual environment not found. Creating 'venv'..."
        if python3 -m venv venv; then
            echo "[VENV] SUCCESS: Virtual environment 'venv' created successfully."
        else
            echo "[VENV] WARNING: Failed to create virtual environment. Falling back to system pip."
        fi
    else
        echo "[VENV] SUCCESS: Virtual environment 'venv' already exists."
    fi

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "[VENV] SUCCESS: Virtual environment activated."
        VENV_ACTIVE=1
    fi
else
    echo "[VENV] INFO: ensurepip not available (Kaggle / managed environment detected)."
    echo "[VENV] INFO: Skipping venv creation — using system pip directly."
fi

echo "=== Step 2: Installing Dependencies ==="
pip install --quiet --upgrade pip
if pip install --quiet -r requirements.txt; then
    echo "[Dependencies] SUCCESS: All Python packages installed successfully."
else
    echo "[Dependencies] FAILURE: Failed to install Python dependencies from requirements.txt."
    exit 1
fi

echo "=== Step 3: Checking System Utilities ==="
# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "[Ollama] Installing Ollama..."
    if curl -fsSL https://ollama.com/install.sh | sh; then
        echo "[Ollama] SUCCESS: Ollama installed successfully."
    else
        echo "[Ollama] FAILURE: Failed to install Ollama."
        exit 1
    fi
else
    echo "[Ollama] SUCCESS: Ollama CLI is already available."
fi

# Check bore tunnel tool
if ! command -v bore &> /dev/null && [ ! -f "/usr/local/bin/bore" ]; then
    echo "[Tunnel] Downloading bore CLI..."
    if wget -q https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-x86_64-unknown-linux-musl.tar.gz -O /tmp/bore.tar.gz &&        tar -xf /tmp/bore.tar.gz -C /usr/local/bin &&        chmod +x /usr/local/bin/bore; then
        echo "[Tunnel] SUCCESS: bore CLI downloaded and installed to /usr/local/bin."
    else
        echo "[Tunnel] FAILURE: Failed to download or install bore CLI."
        exit 1
    fi
else
    echo "[Tunnel] SUCCESS: bore CLI is already available."
fi

echo "=== Step 4: Starting Main Python Application ==="
python main.py
if [ $? -ne 0 ]; then
    echo "[System] FAILURE: main.py exited with an error."
    exit 1
fi
