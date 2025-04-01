import torch
torch.classes.__path__ = []
import streamlit as st
from streamlit_chat import message
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import logging

from main import run_physics_qa_pipeline
from chat_history_manager import ChatHistoryManager

# Set up logging (optional)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------
# Load API key from environment (.env)
# ---------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Check if logging is already configured using a session state flag
if "logging_configured" not in st.session_state:
    class StreamlitHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            if "processing_logs" not in st.session_state:
                st.session_state["processing_logs"] = []
            st.session_state["processing_logs"].append(log_entry)

    # Set up the handler
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setLevel(logging.INFO)
    streamlit_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    # Add handler to the root logger only once
    logging.getLogger().addHandler(streamlit_handler)
    
    # Mark that logging is configured so this block isn't run again
    st.session_state["logging_configured"] = True


# ---------------------
# Gemini OCR Class
# ---------------------
class GeminiOCR:
    def __init__(self):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        
    def extract_text(self, image_data) -> str:
        try:
            image = PIL.Image.open(image_data)
            prompt = "Perform OCR on this image and return the exact text content as it appears, without summarizing or interpreting it."
            response = self.model.generate_content([prompt, image], stream=False)
            log_message("OCR completed for uploaded image.")
            return response.text.strip() if response.text else "No text detected"
        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            log_message(error_msg)
            return error_msg

# Create an instance of GeminiOCR
ocr_processor = GeminiOCR()

# ---------------------
# Initialize Processing Log in Session State
# ---------------------
if "processing_logs" not in st.session_state:
    st.session_state["processing_logs"] = []

# Helper function to log messages for the demo
def log_message(msg):
    st.session_state["processing_logs"].append(msg)
    logger.info(msg)

# ---------------------
# Page & CSS Customization
# ---------------------
st.set_page_config(page_title="Physics Chatbot", page_icon="📘", layout="centered")
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
    background-color: #e6f7ff !important;
    color: #333;
    text-align: right;
}
.stMessage.is-bot {
    background-color: #f1f1f1 !important;
    color: #333;
    text-align: left;
}
/* Override avatar images */
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

st.markdown("<h1>Physics QA Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<h3>Hello! I’m your AI assistant, specialized in Class 12 Physics. Feel free to ask me any question about Class 12 Physics!</h3>", unsafe_allow_html=True)

# -----------------------
# Session State Setup
# -----------------------
if "user_input" not in st.session_state:
    st.session_state["user_input"] = []
if "bot_response" not in st.session_state:
    st.session_state["bot_response"] = []
if "chat_manager" not in st.session_state:
    st.session_state["chat_manager"] = ChatHistoryManager("EM-RAG-Chatbot-main/chat_history.json")
if "session_id" not in st.session_state:
    st.session_state["session_id"] = st.session_state["chat_manager"].get_new_session_id()
if "needs_rerun" not in st.session_state:
    st.session_state["needs_rerun"] = False
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0
if "last_uploaded_file_name" not in st.session_state:
    st.session_state["last_uploaded_file_name"] = None
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""
if "using_extracted_text" not in st.session_state:
    st.session_state["using_extracted_text"] = False
if "last_query" not in st.session_state:
    st.session_state["last_query"] = ""
if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = ""
if "history_loaded" not in st.session_state:
    st.session_state["history_loaded"] = False

# Log that session state has been initialized
# log_message("Session state initialized.")

# -------------------------------
# Load Persistent Chat History from File
# -------------------------------
if not st.session_state["history_loaded"]:
    history = st.session_state["chat_manager"].get_chat_history(st.session_state["session_id"])
    if history and "messages" in history:
        for msg in history["messages"]:
            if msg["role"] == "user":
                st.session_state["user_input"].append(msg["content"])
            elif msg["role"] == "assistant":
                st.session_state["bot_response"].append(msg["content"])
        # log_message("Loaded persistent chat history.")
    st.session_state["history_loaded"] = True
# -------------------------------
# Clear Input if Rerun Flag is Set
# -------------------------------
if st.session_state["needs_rerun"]:
    st.session_state["input_text"] = ""
    st.session_state["needs_rerun"] = False
    # log_message("Cleared input text after rerun.")

# -------------------------------
# Option: Text Input or Image Upload for Question
# -------------------------------
st.markdown("### Enter your question:")
text_query = st.text_input("Type your question here:", key="input_text", placeholder="e.g., Why do astronauts feel weightless?")
uploaded_file = st.file_uploader("Or upload an image of your question:", type=["png", "jpg", "jpeg"], key=f"file_uploader_{st.session_state['file_uploader_key']}")

if uploaded_file is not None:
    current_file_name = uploaded_file.name
    if current_file_name != st.session_state["last_uploaded_file_name"]:
        extracted_text = ocr_processor.extract_text(uploaded_file)
        st.markdown("**Extracted Text:**")
        st.write(extracted_text)
        st.session_state["last_uploaded_file_name"] = current_file_name
        st.session_state["extracted_text"] = extracted_text
        st.session_state["using_extracted_text"] = True
        # log_message(f"Processed new image: {current_file_name}")
    else:
        extracted_text = st.session_state["extracted_text"]
        # log_message("Using cached extracted text.")
else:
    extracted_text = ""
    st.session_state["last_uploaded_file_name"] = None
    st.session_state["using_extracted_text"] = False

if extracted_text and not st.session_state["using_extracted_text"]:
    if st.button("Use extracted text as my question"):
        st.session_state["using_extracted_text"] = True
        # log_message("User chose to use extracted text as query.")
        st.rerun()

if text_query:
    user_question = text_query
    if st.session_state["using_extracted_text"]:
        st.session_state["using_extracted_text"] = False
        st.session_state["file_uploader_key"] += 1
        # log_message("Text query overrides extracted text; resetting file uploader.")
elif st.session_state["using_extracted_text"] and extracted_text:
    user_question = extracted_text
else:
    user_question = None

# -------------------------------
# Display Chat History (in a container)
# -------------------------------
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for i in range(len(st.session_state["bot_response"])):
        message(
            st.session_state["user_input"][i],
            is_user=True,
            key=f"user_{i}",
            avatar_style="human"
        )
        message(
            st.session_state["bot_response"][i],
            key=f"bot_{i}",
            avatar_style="bottts"
        )
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# Process Input and Rerun (with caching)
# -------------------------------
if user_question:
    if "last_query" in st.session_state and st.session_state["last_query"] == user_question:
        answer = st.session_state["last_answer"]
        # log_message("Using cached answer for query.")
    else:
        raw_response = run_physics_qa_pipeline(user_question, st.session_state["session_id"])
        answer = raw_response.strip()
        st.session_state["last_query"] = user_question
        st.session_state["last_answer"] = answer
        # log_message("Processed new query through pipeline.")
    
    st.session_state["user_input"].append(user_question)
    st.session_state["bot_response"].append(answer)
    st.session_state["chat_manager"].update_chat_history(
        st.session_state["session_id"], user_question, answer
    )
    # log_message(f"Updated chat history with query: {user_question}")

    if st.session_state["using_extracted_text"]:
        st.session_state["using_extracted_text"] = False
        st.session_state["file_uploader_key"] += 1
        # log_message("Reset file uploader after processing extracted text.")

    st.session_state["needs_rerun"] = True
    st.rerun()

# -------------------------------
# Display Processing Log for Demo
# -------------------------------
with st.expander("Processing Log"):
    if "processing_logs" in st.session_state and st.session_state["processing_logs"]:
        for log in st.session_state["processing_logs"]:
            st.write(log)
    else:
        st.write("No processing logs available.")
