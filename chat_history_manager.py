import json
import os
import logging
import uuid
from pathlib import Path

class ChatHistoryManager:
    """
    Manages chat history for each session, storing it in a local JSON file.
    All human and AI message pairs are stored without any summarization.
    Each session stores a list of messages under the key "messages".
    Each message is a dictionary with "role" and "content".
    """
    def __new__(cls, *args, **kwargs):
        global _instance
        if _instance is None:
            #logger.info("[ChatHistoryManager SINGLETON] Creating new instance.")
            _instance = super(ChatHistoryManager, cls).__new__(cls)
            # Initialize only once
            _instance._initialized = False
        else:
             #logger.info("[ChatHistoryManager SINGLETON] Returning existing instance.")
             pass
        return _instance

    def __init__(self, history_file: str = "chat_history.json"):
        if self._initialized:
            return # Prevent re-initialization

        #logger.info("[ChatHistoryManager SINGLETON] Initializing instance attributes.")
        self.history_file = Path(history_file)
        #logger.info(f"[ChatHistoryManager DEBUG] Initializing. Attempting to use history file at relative path: {history_file}")
        #logger.info(f"[ChatHistoryManager DEBUG] Absolute path resolved to: {self.history_file.resolve()}")
        self.chat_history = self.load_chat_history()
        #logging(f"[ChatHistoryManager DEBUG] Initial load complete. In-memory history keys: {list(self.chat_history.keys())}")
        self._initialized = True # Mark as initialized

    '''def __init__(self, history_file: str = "chat_history.json"):
        self.history_file = Path(history_file)
        self.chat_history = self.load_chat_history()'''

    def get_new_session_id(self) -> str:
        """Generates a new session ID."""
        return str(uuid.uuid4())

    def load_chat_history(self) -> dict:
        """Loads chat history from a file if it exists; otherwise, returns an empty dict."""
        if self.history_file.exists():
            try:
                content = self.history_file.read_text(encoding="utf-8").strip()
                if not content:
                    return {}
                data = json.loads(content)
                return data if isinstance(data, dict) else {}
            except Exception as e:
                logging.error(f"Error loading chat history: {e}")
                return {}
        return {}


    def save_chat_history(self) -> None:
        """Saves the current chat history to a file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving chat history: {e}")

    def get_chat_history(self, session_id: str) -> dict:
        """
        Retrieve the chat history for a specific session.
        Returns a dictionary with a "messages" key containing the list of messages.
        """
        return self.chat_history.get(session_id, {"messages": []})

    def update_chat_history(self, session_id: str, user_message: str, assistant_message: str) -> None:
        """
        Updates the chat history for the session by appending new user and assistant messages.
        """
        session_data = self.get_chat_history(session_id)
        messages = session_data.get("messages", [])
        if user_message:
            messages.append({"role": "user", "content": user_message})
        if assistant_message:
            messages.append({"role": "assistant", "content": assistant_message})
        session_data["messages"] = messages
        self.chat_history[session_id] = session_data
        self.save_chat_history()
