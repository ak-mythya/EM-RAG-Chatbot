



# chat_history_manager.py

import json
import os

import uuid
from pathlib import Path
import logging






_instance = None # Module-level variable to hold the single instance







class ChatHistoryManager:
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

    def __init__(self, history_file: str = "chat_history_1.json"):
        if self._initialized:
            return # Prevent re-initialization

        #logger.info("[ChatHistoryManager SINGLETON] Initializing instance attributes.")
        self.history_file = Path(history_file)
        #logger.info(f"[ChatHistoryManager DEBUG] Initializing. Attempting to use history file at relative path: {history_file}")
        #logger.info(f"[ChatHistoryManager DEBUG] Absolute path resolved to: {self.history_file.resolve()}")
        self.chat_history = self.load_chat_history()
        #logging(f"[ChatHistoryManager DEBUG] Initial load complete. In-memory history keys: {list(self.chat_history.keys())}")
        self._initialized = True # Mark as initialized



    def get_new_session_id(self) -> str:
        """Generates a new session ID."""
        return str(uuid.uuid4())

    def load_chat_history(self) -> dict:
        """Loads chat history from a file if it exists; otherwise, returns an empty dict."""
        # --- DEBUG logger.info ADDED ---
        #logger.info(f"[ChatHistoryManager DEBUG] Entering load_chat_history for file: {self.history_file.resolve()}")
        # --- END DEBUG ---

        if self.history_file.exists():
            # --- DEBUG logger.info ADDED ---
            #logger.info(f"[ChatHistoryManager DEBUG] File exists: {self.history_file.resolve()}")
            # --- END DEBUG ---
            try:
                content = self.history_file.read_text(encoding="utf-8").strip()
                # --- DEBUG logger.info ADDED ---
                #logger.info(f"[ChatHistoryManager DEBUG] Raw content read from file:\n---\n{content}\n---")
                # --- END DEBUG ---

                if not content:
                    # --- DEBUG logger.info ADDED ---
                    #logger.info("[ChatHistoryManager DEBUG] File content is empty after stripping. Returning empty dict.")
                    # --- END DEBUG ---
                    return {}

                # --- DEBUG logger.info ADDED ---
                #logger.info("[ChatHistoryManager DEBUG] Attempting to parse JSON...")
                # --- END DEBUG ---
                data = json.loads(content)
                # --- DEBUG logger.info ADDED ---
                #logger.info(f"[ChatHistoryManager DEBUG] Successfully parsed JSON data. Type: {type(data)}")
                # Ensure the loaded data is a dictionary
                #if isinstance(data, dict):
                    #logger.info("[ChatHistoryManager DEBUG] Parsed data is a dictionary. Returning it.")
                    #return data
                #else:
                    #logger.info("[ChatHistoryManager DEBUG] Parsed data is NOT a dictionary. Returning empty dict.")
                    #return {}
                # --- END DEBUG ---

            #except json.JSONDecodeError as e:
                # --- DEBUG logger.info ADDED ---
                #logger.info(f"[ChatHistoryManager DEBUG] !!! JSON Decoding Error: {e}")
                # --- END DEBUG ---
                #logging.error(f"Error loading chat history (JSON Decode): {e}")
                #return {}
            except Exception as e:
                # --- DEBUG logger.info ADDED ---
                #logger.info(f"[ChatHistoryManager DEBUG] !!! General Error loading chat history: {e}")
                # --- END DEBUG ---
                logging.error(f"Error loading chat history: {e}")
                return {}
        #else:
            # --- DEBUG logger.info ADDED ---
            #logger.info(f"[ChatHistoryManager DEBUG] History file not found at: {self.history_file.resolve()}. Returning empty dict.")
            # --- END DEBUG ---
        return {}


    def save_chat_history(self) -> None:
        """Saves the current chat history to a file."""
        try:
            # --- DEBUG logger.info ADDED ---
            #logger.info(f"[ChatHistoryManager DEBUG] Saving history to: {self.history_file.resolve()}")
            # --- END DEBUG ---
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, indent=4)
            # --- DEBUG logger.info ADDED ---
            # logger.info(f"[ChatHistoryManager DEBUG] Saved chat history keys: {list(self.chat_history.keys())}") # Optional: can be verbose
            # --- END DEBUG ---
        except Exception as e:
            # --- DEBUG logger.info ADDED ---
            #logging.error(f"[ChatHistoryManager Error] !!! Error saving chat history: {e}")
            # --- END DEBUG ---
            logging.error(f"Error saving chat history: {e}")

    def get_chat_history(self, session_id: str) -> dict:
        """
        Retrieve the chat history for a specific session.
        Returns a dictionary with a "messages" key containing the list of messages.
        """
        # --- DEBUG logger.info ADDED ---
        #logger.info(f"[ChatHistoryManager DEBUG] get_chat_history called for session_id: {session_id}")
        #logger.info(f"[ChatHistoryManager DEBUG] Current in-memory history keys: {list(self.chat_history.keys())}")
        # --- END DEBUG ---
        
        # Check if the session_id exists in the loaded history
        if session_id not in self.chat_history:
             # --- DEBUG logger.info ADDED ---
            #logger.info(f"[ChatHistoryManager DEBUG] Session ID '{session_id}' NOT FOUND in loaded history. Returning default.")
            #print(f"[ChatHistoryManager DEBUG] Session ID '{session_id}' NOT FOUND in loaded history. Returning default.") 
            pass# --- END DEBUG ---

        # Original logic using .get() handles both found and not found cases
        return self.chat_history.get(session_id, {"messages": []})


    def update_chat_history(self, session_id: str, user_message: str, assistant_message: str) -> None:
        """
        Updates the chat history for the session by appending new user and assistant messages.
        """
        # --- DEBUG logger.info ADDED ---
        #logger.info(f"[ChatHistoryManager DEBUG] update_chat_history called for session_id: {session_id}")
        # --- END DEBUG ---
        session_data = self.get_chat_history(session_id) # This will logger.info debug info from get_chat_history
        messages = session_data.get("messages", []) # Safe get, though get_chat_history ensures "messages" exists
        if user_message:
            messages.append({"role": "user", "content": user_message})
        if assistant_message:
            messages.append({"role": "assistant", "content": assistant_message})
        session_data["messages"] = messages
        #logger.info(f"Updated chat history for session {session_id}")  # Original Debugging
       
        self.chat_history[session_id] = session_data
        # --- DEBUG logger.info ADDED ---
        #logger.info(f"[ChatHistoryManager DEBUG] In-memory history updated for {session_id}. Keys now: {list(self.chat_history.keys())}")
        # --- END DEBUG ---
        self.save_chat_history()
        #logger.info(f"Chat history after saving: {self.chat_history}")





