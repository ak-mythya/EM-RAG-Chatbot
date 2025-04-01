import re
import json
import logging
from pathlib import Path
from config import llama_llm, client
from langchain.schema import SystemMessage
from chat_history_manager import ChatHistoryManager
import uuid

class QueryClassifier:
    """
    Uses an LLM to classify the user query as either 'knowledge' (requires retrieval)
    or 'discussion' (direct conversation, retrieval skipped).
    """

    def __init__(self):
        current_dir = Path(__file__).resolve().parent
        # This prompt file should instruct the LLM to output JSON with a key "query_type"
        # e.g., {"query_type": "knowledge"} or {"query_type": "discussion"}
        self.prompt_path = "system_prompts/query_classification.txt"
        self.chat_history_manager = ChatHistoryManager()

    def run(self, state: dict) -> dict:
        session_id = state.get("keys", {}).get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())  # Generate a new UUID session_id
            state.setdefault("keys", {})["session_id"] = session_id
            logging.info(f"Generated new session ID: {session_id}")

        # Load chat history from the JSON file using the correct key
        raw_history = self.chat_history_manager.get_chat_history(session_id)["messages"]
        # Format the chat history into a string (if needed for the prompt)
        chat_history = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in raw_history]
        )

        logging.info("[QueryClassifier] Loaded chat history.")

        # Update the state with the loaded chat history
        state.setdefault("keys", {})["chat_history"] = chat_history

        question = state.get("keys", {}).get("question", "").strip()

        logging.info(f"[QueryClassifier] Classifying user query - {question}.")

        if not question:
            logging.error("Empty user query in classification; defaulting to 'discussion'.")
            state.setdefault("keys", {})["query_type"] = "discussion"
            return state

        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except Exception as e:
            logging.error(f"Error reading query classification prompt: {e}")
            system_prompt = ""

        # Format the prompt: instruct the LLM to decide whether the query is "knowledge" or "discussion"
        classification_prompt = system_prompt.format(
            chat_history=chat_history,
            user_query=question
        )

        try:
            print(classification_prompt)
            response = client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp-01-21", 
                contents=classification_prompt
            )
            response_text = response.text
            # Expect a JSON block like: {"query_type": "knowledge"}
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                logging.info(f"[QueryClassifier] Classification JSON: {json_str}")
                try:
                    result = json.loads(json_str)
                except json.decoder.JSONDecodeError as e:
                    logging.error(f"JSON decoding failed: {e}")
                    result = {"query_type": "knowledge"}
            else:
                logging.error("No JSON block found in LLM response; defaulting to 'knowledge'.")
                result = {"query_type": "knowledge"}
        except Exception as e:
            logging.error(f"Error in query classification: {e}")
            result = {"query_type": "knowledge"}

        query_type = result.get("query_type", "knowledge").strip().lower()
        if query_type not in ["knowledge", "discussion"]:
            query_type = "knowledge"

        state.setdefault("keys", {})["query_type"] = query_type
        logging.info(f"[QueryClassifier] Query classified as: {query_type}")
        return state
