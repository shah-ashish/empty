import time
import sys
import config
from services.ollama_service import start_ollama, ensure_model_pulled
from services.litellm_service import start_litellm
from services.logging_proxy import start_logging_proxy
from services.tunnel_service import start_bore_tunnel

def main():
    print("==================================================")
    print(f" Launching Proxy Chain for Model: {config.MODEL_NAME}")
    print("==================================================")

    try:
        # 1. Start Ollama and pull model
        ollama_proc = start_ollama()
        ensure_model_pulled()

        # 2. Start LiteLLM proxy
        litellm_proc = start_litellm()

        # 3. Start Logging Proxy
        start_logging_proxy()

        # 4. Start Tunnel
        start_bore_tunnel()

        print("[System] SUCCESS: All services initialized successfully. Tailing logs below...
")
        
        # Tail Log File to keep session alive
        with open(config.LOG_FILE, "a"):
            pass

        with open(config.LOG_FILE, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    print(line, end="")
                else:
                    time.sleep(0.3)

    except KeyboardInterrupt:
        print("
[System] Shutting down services cleanly...")
        litellm_proc.terminate()
        ollama_proc.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"
[System] FAILURE: Project startup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
