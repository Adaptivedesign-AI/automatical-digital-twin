import gradio as gr
import os
from openai import OpenAI

# 设置 OpenRouter 客户端
client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# system prompt（你可以从 student_prompt.txt 读取）
with open("student_prompt.txt", "r") as f:
    system_prompt = f.read().strip()

student_avatar_url = "https://raw.githubusercontent.com/Adaptivedesign-AI/Digital-twin-003/main/image.png"

# 所有支持的模型（你可以自行增删）
model_choices = [
    "mistralai/mistral-7b-instruct",
    "openchat/openchat-3.5-1210",
    "google/gemma-7b-it",
    "meta-llama/llama-2-7b-chat",
]

# 核心对话函数（增加模型参数）
def chat_with_student003(message, history, selected_model):
    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, bot_reply in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_reply})
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error:", e)
        return "Sorry, I'm having trouble responding right now."

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Talk to Student003 — A Digital Twin")
    gr.Markdown("Select a model and start chatting with a simulated student.")

    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=model_choices,
            label="Choose LLM Model",
            value="mistralai/mistral-7b-instruct"
        )

    chatbot = gr.Chatbot(label="Conversation", avatar_images=(None, student_avatar_url))
    msg = gr.Textbox(placeholder="Type your message here...")
    clear = gr.Button("Clear Conversation")

    def respond(message, chat_history, selected_model):
        bot_message = chat_with_student003(message, chat_history, selected_model)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot, model_dropdown], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

# 启动 Render 服务器（用于部署）
if __name__ == "__main__":
    demo.queue(api_open=True).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
    
