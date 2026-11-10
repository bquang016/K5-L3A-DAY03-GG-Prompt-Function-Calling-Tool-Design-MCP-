import subprocess
import time
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent

# 1. Start Streamlit
print("Starting Streamlit on port 8501...")
streamlit_proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
    cwd=str(ROOT),
)

time.sleep(4)

# 2. Start cloudflared tunnel
cloudflared_bin = ROOT / "cloudflared.exe"
log_file = ROOT / "tunnel.log"
if log_file.exists():
    try:
        log_file.unlink()
    except Exception:
        pass

print("Starting Cloudflare Tunnel...")
tunnel_proc = subprocess.Popen(
    [str(cloudflared_bin), "tunnel", "--url", "http://localhost:8501"],
    cwd=str(ROOT),
    stdout=open(log_file, "w", encoding="utf-8"),
    stderr=subprocess.STDOUT,
)

# 3. Poll log file for trycloudflare.com URL
tunnel_url = None
for _ in range(30):
    time.sleep(1)
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
        if match:
            tunnel_url = match.group(0)
            break

if tunnel_url:
    print(f"\n==================================================")
    print(f"SUCCESS! Public Tunnel URL: {tunnel_url}")
    print(f"==================================================\n", flush=True)
    (ROOT / "tunnel_url.txt").write_text(tunnel_url, encoding="utf-8")
else:
    print("\nCould not find URL yet. Recent log:", flush=True)
    if log_file.exists():
        print(log_file.read_text(encoding="utf-8", errors="ignore")[-1000:], flush=True)

# Keep process alive
try:
    while True:
        time.sleep(1)
        if tunnel_proc.poll() is not None:
            print("Tunnel process exited unexpectedly.")
            break
        if streamlit_proc.poll() is not None:
            print("Streamlit process exited unexpectedly.")
            break
except KeyboardInterrupt:
    tunnel_proc.terminate()
    streamlit_proc.terminate()
