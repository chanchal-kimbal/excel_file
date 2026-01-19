import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "streamlit", "run", "display.py"
])