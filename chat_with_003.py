import gradio as gr
import os
import requests

# 读取系统提示词
with open("student_prompt.txt", "r") as f:
    system_prompt = f.read().strip()

student_avatar_url = "https://raw.githubusercontent.com/Adaptivedesign-AI/Digital-twin-003/main/image.png"

# ✅ 所有 OpenRouter 上可用的大模型（截至 2025-05）
model_choices = [
    "mistralai/mistral-7b-instruct",
    "openchat/openchat-3.5-1210",
    "google/gemma-7b-it",
    "meta-llama/llama-2-7b-chat",
    "zero-one-ai/Yi-1.5-9B-Chat",
    "nousresearch/nous-hermes-2-mistral",
    "meta-llama/Meta-Llama-3-8B-Instruct"
]

# Improve error handling in chat_with_student003 function
def chat_with_student003(message, history, selected_model):
    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, bot_reply in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_reply})
    messages.append({"role": "user", "content": message})
    
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "HTTP-Referer": "https://chat-with-003-openrouter.onrender.com",
        "X-Title": "Digital-Twin-003",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": 0.7
    }
    
    try:
        print(f"\n🧪 正在调用模型: {selected_model}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"🔢 状态码: {response.status_code}")
        
        # 详细记录响应内容以便调试
        if response.status_code != 200:
            print(f"❌ 错误响应: {response.text}")
            return f"模型 {selected_model} 返回错误: HTTP {response.status_code}"
            
        result = response.json()
        print(f"📨 响应成功: {result.keys()}")
        
        # 检查响应格式是否符合预期
        if "choices" not in result or len(result["choices"]) == 0:
            print(f"❌ 响应格式错误: {result}")
            return f"模型 {selected_model} 返回了意外的响应格式"
            
        return result["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return f"模型 {selected_model} 请求超时，请稍后再试"
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return f"与模型 {selected_model} 通信时出现网络问题"
    except Exception as e:
        print(f"❌ 其他异常: {e}")
        return f"使用模型 {selected_model} 时出现错误: {str(e)}"
        
# ✅ 构建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Talk to Student003 — A Digital Twin")
    gr.Markdown("Compare different open LLMs in a unified interface.")

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

# ✅ 启动服务器（兼容 Render）
if __name__ == "__main__":
    demo.queue(api_open=True).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
