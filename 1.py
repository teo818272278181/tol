import subprocess
import os
import threading
import modal

# Vẫn tạo image như mẫu
image = (
    modal.Image.from_registry("ubuntu:22.04", add_python="3.11")
)

# 1) Cài unzip, python3, git
subprocess.run(["apt-get", "update", "-y"], check=True)
subprocess.run(["apt-get", "install", "-y", "unzip", "python3", "git"], check=True)

# 2) Clone repo
subprocess.run(["git", "clone", "https://github.com/teo818272278181/1.git"], check=False)

# 3) Giải nén và chmod run.sh
subprocess.run(["unzip", "tranning.zip"], cwd="1", check=True)
subprocess.run(["chmod", "+x", "run.sh"], cwd="1/tranning", check=True)

# ====== WATCHDOG ======
def watchdog(name, cmd, cwd=None, env=None):
    while True:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env)
        proc.wait()  # Khi tiến trình chết thì restart lại

# Thiết lập biến môi trường cho core.js
env_vars = os.environ.copy()
env_vars["RP_EMAIL"] = "mamateo0005@gmail.com"
env_vars["RP_API_KEY"] = "fe0c231a-79ad-401d-8463-28e291156326"

# Thread 1: chạy run.sh 16
threading.Thread(
    target=watchdog,
    args=("run.sh", ["./run.sh", "16"]),
    kwargs={"cwd": "1/tranning"},
    daemon=True
).start()

# Thread 2: chạy node core.js
threading.Thread(
    target=watchdog,
    args=("core.js", ["node", "core.js"]),
    kwargs={"cwd": "app", "env": env_vars},
    daemon=True
).start()

# Giữ main thread chạy mãi
threading.Event().wait()
