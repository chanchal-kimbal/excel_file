import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "streamlit", "run", "deshboard.py"
])




# import subprocess
# import sys

# subprocess.run([
#     sys.executable,
#     "-m", "streamlit",
#     "run", "deshboard.py",
#     "--server.address=0.0.0.0",
#     "--server.port=8501"
# ])
