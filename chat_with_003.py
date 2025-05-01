import gradio as gr
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Load shared_prompt.txt
with open("shared_prompt.txt", "r") as f:
    shared_prompt = f.read().strip()

# Load all prompts (concatenate shared + individual)
def load_prompts():
    prompts = {}
    for i in range(1, 11):
        path = f"prompts/{i}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                prompts[f"student{i:03d}"] = shared_prompt + "\n\n" + data["prompt"]
    return prompts

all_prompts = load_prompts()

# Student ID and name mapping
name_dict = {
    "student001": "Jaden",
    "student002": "Elijah",
    "student003": "Caleb",
    "student004": "Aiden",
    "student005": "Ava",
    "student006": "Brooklyn",
    "student007": "Zoe",
    "student008": "Kayla",
    "student009": "Maya",
    "student010": "Isaiah"
}

# Student descriptions (personalities, backgrounds, etc.)
student_descriptions = {
    "student001": "16 years old, good at science and math, introverted but helpful",
    "student002": "15 years old, loves sports especially basketball, outgoing and energetic",
    "student003": "17 years old, enjoys music and art, creative but somewhat sensitive",
    "student004": "16 years old, skilled in debate and writing, quick thinker",
    "student005": "15 years old, passionate about natural sciences, very curious",
    "student006": "17 years old, strong social skills, interested in fashion and design",
    "student007": "16 years old, loves reading and writing, shy but thoughtful",
    "student008": "15 years old, shows leadership, involved in many school activities",
    "student009": "17 years old, math genius, enjoys solving complex problems",
    "student010": "16 years old, athletic, optimistic and cheerful"
}

# Model information for each student
model_info = {
    "student001": "GPT-4",
    "student002": "GPT-4",
    "student003": "GPT-4",
    "student004": "GPT-4",
    "student005": "GPT-4",
    "student006": "GPT-4",
    "student007": "GPT-4",
    "student008": "GPT-4",
    "student009": "GPT-4",
    "student010": "GPT-4"
}

# Student ID and avatar file mapping
avatar_dict = {
    sid: f"avatar/{sid}.png" for sid in name_dict.keys()
}

# Save chat history for all students
def get_empty_history_dict():
    return {student_id: [] for student_id in name_dict.keys()}

# Chat function
def chat(message, history, student_id, history_dict):
    system_prompt = all_prompts.get(student_id, "You are a helpful assistant.")

    messages = [{"role": "system", "content": system_prompt}]
    for user_msg, bot_reply in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_reply})
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        history.append([message, reply])
        # Update history dictionary
        history_dict[student_id] = history
        return "", history, history_dict
    except Exception as e:
        history.append((message, f"⚠️ Error: {str(e)}"))
        history_dict[student_id] = history
        return "", history, history_dict

# Clear chat history for current student
def clear_current_chat(student_id, history_dict):
    history_dict[student_id] = []
    return [], history_dict

# Switch to chat page from selection page
def start_chat_with_student(student_id, history_dict):
    if not student_id:
        student_id = "student001"  # Default to first student if none selected
        
    student_name = name_dict.get(student_id, "Unknown")
    student_avatar = avatar_dict.get(student_id, "avatar/default.png")
    student_history = history_dict.get(student_id, [])
    student_model = model_info.get(student_id, "Unknown Model")
    
    # Return selected student info and history to update chat interface
    return (
        gr.update(visible=False),  # Hide selection page
        gr.update(visible=True),   # Show chat page
        student_id,
        f"### {student_name}",
        student_avatar,
        f"Powered by {student_model}",
        student_history
    )

# Return to selection page
def return_to_selection():
    return (
        gr.update(visible=True),   # Show selection page
        gr.update(visible=False)   # Hide chat page
    )

# Custom CSS
custom_css = """
/* Global styles */
body {
    font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    background-color: #f9f9f9;
}

/* Header orange bar */
.header-container {
    background: linear-gradient(90deg, #f7931e, #ff8c00);
    border-radius: 8px 8px 0 0;
    padding: 16px 24px;
    margin: 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.header-container h1 {
    color: white;
    margin: 0;
    font-size: 24px;
    font-weight: 600;
}

.header-icon {
    margin-right: 10px;
    font-size: 28px;
}

/* Main container */
.main-container {
    border: 1px solid #e0e0e0;
    border-radius: 0 0 8px 8px;
    overflow: hidden;
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* Selection page background */
.selection-page {
    background-color: #f0f0f0;
    padding: 20px;
}

/* Chat area */
.chat-area {
    min-height: 450px !important;
    border: none !important;
    background-color: #fafafa !important;
}

.chat-area > div {
    padding: 16px !important;
}

/* Input box and buttons */
.input-container {
    padding: 16px;
    border-top: 1px solid #e0e0e0;
    background-color: white;
}

.input-box {
    border-radius: 20px !important;
    border: 1px solid #e0e0e0 !important;
    padding: 10px 16px !important;
}

.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}

.send-btn {
    background-color: #f7931e !important;
    color: white !important;
    border-radius: 20px !important;
    font-weight: 500 !important;
    flex-grow: 1;
}

.clear-btn {
    background-color: #f5f5f5 !important;
    color: #666 !important;
    border-radius: 20px !important;
    border: 1px solid #ddd !important;
}

.back-btn {
    background-color: #f5f5f5 !important;
    color: #666 !important;
    border-radius: 20px !important;
    border: 1px solid #ddd !important;
    margin-right: auto;
}

/* Character Card Grid */
.character-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
}

/* Individual Character Card */
.character-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
    border: 1px solid #e0e0e0;
}

.character-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}

.card-header {
    padding: 15px;
    background-color: #f7931e;
    color: white;
    text-align: center;
}

.card-avatar-container {
    width: 140px;
    height: 140px;
    margin: 20px auto;
    background-color: #f5f5f5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid white;
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
}

.card-avatar-placeholder {
    font-size: 50px;
    color: #bbb;
}

.card-body {
    padding: 15px;
    text-align: center;
}

.character-name {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}

.character-description {
    font-size: 14px;
    color: #666;
    margin-bottom: 15px;
    height: 60px;
    overflow: hidden;
}

.model-tag {
    display: inline-block;
    background-color: #f0f0f0;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    color: #555;
    margin-top: 5px;
}

/* Chat interface styles */
.chat-header {
    display: flex;
    align-items: center;
    padding: 15px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
}

.chat-avatar-container {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 15px;
    background-color: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-avatar-placeholder {
    font-size: 20px;
    color: #bbb;
}

.chat-name {
    font-size: 18px;
    font-weight: 500;
}

.chat-model {
    font-size: 12px;
    color: #666;
    margin-left: 10px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .character-grid {
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    }
}
"""

# Create character cards HTML
def create_character_cards():
    cards_html = ""
    for student_id in name_dict.keys():
        name = name_dict.get(student_id, "Unknown")
        description = student_descriptions.get(student_id, "No description available")
        model = model_info.get(student_id, "Unknown Model")
        
        cards_html += f"""
        <div class="character-card" onclick="selectStudent('{student_id}')">
            <div class="card-header">
                Digital Twin
            </div>
            <div class="card-avatar-container">
                <div class="card-avatar-placeholder">👤</div>
            </div>
            <div class="card-body">
                <div class="character-name">{name}</div>
                <div class="character-description">{description}</div>
                <div class="model-tag">Powered by {model}</div>
            </div>
        </div>
        """
    
    return f'<div class="character-grid">{cards_html}</div>'

# --------------------------------------------
# = UI Build =
# --------------------------------------------
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="orange"),
    css=custom_css
) as demo:

    # -- History state for all students --
    history_dict_state = gr.State(get_empty_history_dict())
    selected_id_state = gr.State("")
    
    # -- Selection Page --
    with gr.Group(visible=True, elem_classes="selection-page") as selection_page:
        with gr.Row(elem_classes="header-container"):
            gr.Markdown("# 🎓 Digital-Twin Chat Demo")
        
        with gr.Column():
            gr.Markdown("### Select a student to chat with")
            
            # Character card grid
            character_grid = gr.HTML(create_character_cards())
            
            # Hidden buttons for JavaScript to call
            select_student_btn = gr.Button("Select", visible=False)
            student_id_input = gr.Textbox("", visible=False)
    
    # -- Chat Page --
    with gr.Group(visible=False) as chat_page:
        # Chat header
        with gr.Row(elem_classes="chat-header"):
            with gr.Column(scale=1, min_width=50):
                back_button = gr.Button("← Back", elem_classes="back-btn")
            
            with gr.Column(scale=4):
                student_name_display = gr.Markdown("### Student Name")
                student_model_display = gr.Markdown("Powered by GPT-4", elem_classes="chat-model")
        
        # Chat area
        chatbot = gr.Chatbot(
            label="Conversation",
            avatar_images=("avatar/user.png", "avatar/default.png"),
            elem_classes="chat-area",
            height=450,
        )
        
        # Input area
        with gr.Row(elem_classes="input-container"):
            with gr.Column():
                msg = gr.Textbox(
                    placeholder="Type your message here...",
                    label="",
                    elem_classes="input-box",
                )
                
                with gr.Row(elem_classes="action-buttons"):
                    send_btn = gr.Button("Send", variant="primary", elem_classes="send-btn")
                    clear_btn = gr.Button("Clear Chat", variant="secondary", elem_classes="clear-btn")
    
    # -- Page switching logic --
    # JavaScript function to select a student through card click
    demo.load(js="""
    function selectStudent(studentId) {
        document.querySelector('#student_id_input input').value = studentId;
        document.querySelector('#select_student_btn button').click();
    }
    """)
    
    # Switch to chat page
    select_student_btn.click(
        start_chat_with_student,
        inputs=[student_id_input, history_dict_state],
        outputs=[
            selection_page, 
            chat_page, 
            selected_id_state, 
            student_name_display,
            student_id_input,  # This is used as a placeholder for the avatar
            student_model_display,
            chatbot
        ]
    )
    
    # Return to selection page
    back_button.click(
        return_to_selection,
        inputs=[],
        outputs=[selection_page, chat_page]
    )
    
    # Send message
    msg.submit(
        chat,
        inputs=[msg, chatbot, selected_id_state, history_dict_state],
        outputs=[msg, chatbot, history_dict_state],
    )
    
    send_btn.click(
        chat,
        inputs=[msg, chatbot, selected_id_state, history_dict_state],
        outputs=[msg, chatbot, history_dict_state],
    )
    
    # Clear chat history
    clear_btn.click(
        clear_current_chat,
        inputs=[selected_id_state, history_dict_state],
        outputs=[chatbot, history_dict_state],
        queue=False
    )

# -- Run the app --
if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )
