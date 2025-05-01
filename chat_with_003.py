from openai import OpenAI
import gradio as gr
import os

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],  
    base_url="https://openrouter.ai/api/v1"
)

# Student003's system prompt (you'll fill this with your specific details)
system_prompt = """

"""

student_avatar_url = "https://raw.githubusercontent.com/Adaptivedesign-AI/Digital-twin-003/main/image.png"

def chat_with_student003(message, history):
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for user_msg, bot_reply in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_reply})
    
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        print("Error:", e)
        return "Sorry, I'm having trouble responding right now."

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Talk to Student003 🧑‍🎓")

    chatbot = gr.Chatbot(label="Conversation", avatar_images=(None, student_avatar_url))
    msg = gr.Textbox(placeholder="Type your message...")
    clear = gr.Button("Clear")

    def respond(message, chat_history):
        bot_message = chat_with_student003(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

# Render deployment settings
if __name__ == "__main__":
    demo.queue(api_open=True).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
    app.queue(api_open=True)
    app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)), share=True)
