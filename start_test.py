import subprocess
import sys
from pathlib import Path

app_path = Path(__file__).with_name("test_app.py")

subprocess.run([
    sys.executable, "-m", "streamlit", "run", str(app_path)
])
#test