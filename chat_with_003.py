import gradio as gr
import os
import requests
import time

# 读取系统提示词
with open("student_prompt.txt", "r") as f:
    system_prompt = f.read().strip()

student_avatar_url = "https://raw.githubusercontent.com/Adaptivedesign-AI/Digital-twin-003/main/image.png"

# 固定使用单一模型
model = "meta-llama/llama-3-8b-instruct"

def chat_with_student003(message, history):
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
    
    # 简化负载，只包含必要参数
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        print(f"\n🧪 使用模型: {model}")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"🔢 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 错误响应: {response.text}")
            error_message = f"错误 (HTTP {response.status_code}): "
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    error_message += error_data["error"]["message"]
            except:
                error_message += "未知错误"
            return error_message
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.Timeout:
        return "请求超时，请稍后再试"
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return f"发生错误: {str(e)}"

# 简化 Gradio 界面 - 移除了模型选择
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Talk to Student003 — A Digital Twin")
    
    chatbot = gr.Chatbot(label="Conversation", avatar_images=(None, student_avatar_url))
    msg = gr.Textbox(placeholder="Type your message here...")
    clear = gr.Button("Clear Conversation")
    
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history
        
        bot_message = chat_with_student003(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

# 启动服务器
if __name__ == "__main__":
    demo.queue(api_open=True).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
