
import torch
torch.classes.__path__ = []
import streamlit as st
from streamlit_chat import message
import json


from main import run_physics_qa_pipeline
from chat_history_manager import ChatHistoryManager

# ---------------------
# Page & CSS Customization
# ---------------------
st.set_page_config(page_title="Physics Chatbot", page_icon="📘", layout="centered")

# Inject custom CSS for a cleaner, more modern UI and custom avatars.
st.markdown("""
<style>
/* Overall body styling */
body {
    background: linear-gradient(135deg, #f7f9fc, #cfd9df) !important;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* Remove default Streamlit padding */
.main .block-container {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    margin: 0 auto;
}

/* Title styling */
h1 {
    text-align: center;
    font-weight: 700;
    color: #333;
    margin-bottom: 0.25rem;
}

/* Subheading styling */
h3 {
    text-align: center;
    color: #555;
    font-weight: 400;
    margin-top: 0;
    margin-bottom: 0.5rem;
}

/* Chat container styling */
.chat-container {
    max-width: 700px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-top: 0.5rem;
}

/* Chat input styling */
.stTextInput > div > div > input {
    border-radius: 0.5rem;
    border: 1px solid #ccc;
    padding: 0.75rem;
    font-size: 1rem;
    background-color: #ffffff;
    width: 100%;
}

/* Chat bubble styling */
.stMessage {
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    line-height: 1.4;
}

.stMessage.is-user {
    background-color: #e6f7ff !important; /* Light blue for user messages */
    color: #333;
    text-align: right;
}

.stMessage.is-bot {
    background-color: #f1f1f1 !important; /* Light gray for bot messages */
    color: #333;
    text-align: left;
}

/* Override avatar images using attribute selectors */
/* Assuming message() creates an element with an id starting with the key provided */
div[id^="user_"] img {
    content: url("https://example.com/male_avatar.png") !important;
    width: 40px;
    height: 40px;
    border-radius: 50%;
}

div[id^="bot_"] img {
    content: url("https://example.com/female_avatar.png") !important;
    width: 40px;
    height: 40px;
    border-radius: 50%;
}
</style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown("<h1>Physics QA Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<h3>Hello! I’m your AI assistant, specialized in Class 12 Physics. Feel free to ask me any question about Class 12 Physics!</h3>", unsafe_allow_html=True)

# -----------------------
# 1. Session State Setup
# -----------------------
if "user_input" not in st.session_state:
    st.session_state["user_input"] = []
if "bot_response" not in st.session_state:
    st.session_state["bot_response"] = []
if "chat_manager" not in st.session_state:
    st.session_state["chat_manager"] = ChatHistoryManager("chat_history.json")
if "session_id" not in st.session_state:
    st.session_state["session_id"] = st.session_state["chat_manager"].get_new_session_id()
if "needs_rerun" not in st.session_state:
    st.session_state["needs_rerun"] = False
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

# -------------------------------
# 2. Clear Input if Rerun Flag is Set
# -------------------------------
if st.session_state["needs_rerun"]:
    st.session_state["input_text"] = ""
    st.session_state["needs_rerun"] = False

# ---------------------
# 3. Display Chat History (in a container)
# ---------------------
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for i in range(len(st.session_state["bot_response"])):
        # User message with a simple avatar (will be overridden by our CSS)
        message(
            st.session_state["user_input"][i],
            is_user=True,
            key=f"user_{i}",
            avatar_style="big-smile"
            
        )
        # Bot message with a simple avatar (will be overridden by our CSS)
        message(
            st.session_state["bot_response"][i],
            key=f"bot_{i}",
            avatar_style="avataaars"
            #avatar_style="adventurer"
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------
# 4. Chat Input Widget
# ---------------------
user_text = st.text_input(
    "Have a question on Class 12 Physics? Ask now!",
    key="input_text",
    placeholder="Type your question and press Enter...",
)

# -------------------------------
# 5. Process Input and Rerun
# -------------------------------
if user_text:
    raw_response = run_physics_qa_pipeline(user_text, st.session_state["session_id"])
    answer = raw_response.strip()
    
    # Save messages in session state
    st.session_state["user_input"].append(user_text)
    st.session_state["bot_response"].append(answer)
    
    # Update persistent chat history
    st.session_state["chat_manager"].update_chat_history(
        st.session_state["session_id"], user_text, answer
    )
    
    # Set flag to clear input on next run and force a rerun
    st.session_state["needs_rerun"] = True
    st.rerun()









