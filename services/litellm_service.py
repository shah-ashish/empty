import subprocess
import time
import requests
import config

def generate_litellm_yaml():
    """Generates LiteLLM YAML config using values from config.py."""
    yaml_content = f"""model_list:
  - model_name: {config.MODEL_NAME}
    litellm_params:
      model: ollama_chat/{config.MODEL_NAME}
      api_base: {config.OLLAMA_BASE_URL}
      num_ctx: {config.NUM_CTX}
      temperature: {config.TEMPERATURE}
      repeat_penalty: {config.REPEAT_PENALTY}
      think: {str(config.THINK).lower()}
      num_predict: -1
    model_info:
      supports_function_calling: true

litellm_settings:
  drop_params: true
"""
    with open("litellm_config.yaml", "w") as f:
        f.write(yaml_content)
    print("[LiteLLM] SUCCESS: Config 'litellm_config.yaml' written successfully.")

def start_litellm():
    """Launches the LiteLLM proxy process."""
    generate_litellm_yaml()
    print(f"[LiteLLM] Starting LiteLLM proxy on port {config.LITELLM_PORT}...")
    proc = subprocess.Popen(
        ["litellm", "--config", "litellm_config.yaml", "--port", str(config.LITELLM_PORT)]
    )

    for _ in range(60):
        try:
            res = requests.get(f"{config.LITELLM_BASE_URL}/health/liveliness", timeout=1)
            if res.status_code == 200:
                print("[LiteLLM] SUCCESS: Proxy is up and responsive.")
                return proc
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    print("[LiteLLM] WARNING: Proxy health check timed out. Proceeding anyway...")
    return proc
