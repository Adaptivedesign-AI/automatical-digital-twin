import gradio as gr
import os
import requests
import json
import time

# 读取系统提示词
with open("student_prompt.txt", "r") as f:
    system_prompt = f.read().strip()

student_avatar_url = "https://raw.githubusercontent.com/Adaptivedesign-AI/Digital-twin-003/main/image.png"

# 更新为最新的模型ID (2025-05的可用模型)
model_choices = [
    "mistralai/mistral-7b-instruct",           # 这个工作正常
    "openchat/openchat-3.5-0106",              # 使用更新版本的OpenChat
    "google/gemma-3-27b-it:free",              # 更新为Gemma 3 (免费层级)
    "meta-llama/llama-3-8b-instruct",          # 更新为Llama 3
    "01-ai/yi-1.5-9b-chat",                    # 正确格式
    "mistralai/mixtral-8x7b-instruct",         # 替代我们能找到的模型
    "anthropic/claude-3-haiku-20240307"        # 添加可靠的替代模型
]

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
    
    # 添加错误重试机制
    max_retries = 2
    retry_delay = 1.5
    
    for attempt in range(max_retries + 1):
        try:
            print(f"\n🧪 尝试使用模型: {selected_model} (尝试 {attempt+1}/{max_retries+1})")
            
            # 构建请求负载
            payload = {
                "model": selected_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                # 添加模型回退选项，提高可靠性
                "models": [selected_model, "mistralai/mistral-7b-instruct"],
                # 更灵活的提供商设置
                "provider": {
                    "data_collection": "allow",  # 允许数据收集增加可用性
                    "require_parameters": False  # 允许部分参数不支持
                }
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30  # 较短超时，启用重试机制
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            
            # 有些错误可以重试
            if response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries:
                error_msg = f"请求失败 (HTTP {response.status_code}): {response.text} - 将在 {retry_delay}秒后重试..."
                print(error_msg)
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
                continue
                
            # 解析错误响应
            error_text = "未知错误"
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    error_text = error_data["error"]["message"]
            except:
                error_text = response.text[:100] + "..." if len(response.text) > 100 else response.text
                
            return f"模型 {selected_model} 返回错误: HTTP {response.status_code} - {error_text}"
            
        except Exception as e:
            if attempt < max_retries:
                print(f"❌ 异常: {str(e)} - 将在 {retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
                continue
            return f"使用模型 {selected_model} 时出现错误: {str(e)}"

# Gradio 界面构建
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
    
    # 添加模型状态指示器
    model_status = gr.Markdown("💡 **提示**: 如果某个模型无法使用，请尝试其他模型")
    
    def respond(message, chat_history, selected_model):
        if not message.strip():
            return "", chat_history
        
        bot_message = chat_with_student003(message, chat_history, selected_model)
        chat_history.append((message, bot_message))
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot, model_dropdown], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

# 启动服务器
if __name__ == "__main__":
    demo.queue(api_open=True).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
