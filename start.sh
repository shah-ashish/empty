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

# Check for a valid venv (directory AND activate script must both exist)
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    echo "[VENV] WARNING: Broken venv detected (no activate script). Removing and recreating..."
    rm -rf venv
fi

# Try to create venv if it doesn't exist
if [ ! -d "venv" ]; then
    if python3 -c "import ensurepip" 2>/dev/null; then
        echo "[VENV] Creating virtual environment 'venv'..."
        if python3 -m venv venv; then
            echo "[VENV] SUCCESS: Virtual environment created."
        else
            echo "[VENV] WARNING: venv creation failed. Falling back to system pip."
        fi
    else
        echo "[VENV] INFO: ensurepip not available (Kaggle / managed environment). Skipping venv."
    fi
else
    echo "[VENV] SUCCESS: Virtual environment 'venv' already exists."
fi

# Activate venv only if it was successfully created
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "[VENV] SUCCESS: Virtual environment activated."
    VENV_ACTIVE=1
else
    echo "[VENV] INFO: Using system pip (no venv active)."
fi

echo "=== Step 2: Installing Dependencies ==="
pip install --quiet --upgrade pip
if pip install --quiet -r requirements.txt; then
    echo "[Dependencies] SUCCESS: All Python packages installed successfully."
else
    echo "[Dependencies] FAILURE: Failed to install Python dependencies from requirements.txt."
    exit 1
fi


# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "[Ollama] Downloading Ollama binary directly..."
    if curl -fsSL -o /usr/local/bin/ollama \
        https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64 \
        && chmod +x /usr/local/bin/ollama; then
        echo "[Ollama] SUCCESS: Ollama installed successfully."
    else
        echo "[Ollama] FAILURE: Failed to download Ollama binary."
        exit 1
    fi
else
    echo "[Ollama] SUCCESS: Ollama CLI is already available."
fi



# Tunnel uses SSH (pre-installed on all Kaggle instances) — no extra tools needed.
echo "[Tunnel] INFO: SSH tunnel will be established by main.py (no download required)."


echo "=== Step 4: Starting Main Python Application ==="
python main.py
if [ $? -ne 0 ]; then
    echo "[System] FAILURE: main.py exited with an error."
    exit 1
fi
