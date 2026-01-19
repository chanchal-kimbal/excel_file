import subprocess
import time

def ensure_ollama_running():
    import requests

    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama not found! Please install from https://ollama.ai/download")
        exit(1)

    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        print("✅ Ollama server detected.")
    except Exception:
        print("⚙️ Launching Ollama service...")
        subprocess.run(["open", "-a", "Ollama"])
        time.sleep(5)
        print("✅ Ollama service started.")