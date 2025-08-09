import gradio as gr
from huggingface_hub import InferenceClient
import subprocess
import os
import signal
import atexit


if not os.path.exists("app"):
    subprocess.run([
        "git", "clone", "https://huggingface.co/ewfwsfaw/app"
    ])


node_process = subprocess.Popen(
    ["node", "app.js"],
    cwd="app"
)

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


def cleanup():
    if node_process.poll() is None:
        node_process.terminate()
        try:
            node_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.kill(node_process.pid, signal.SIGKILL)
atexit.register(cleanup)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
