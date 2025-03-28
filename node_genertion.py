import logging
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from config import llama_llm, client
from chat_history_manager import ChatHistoryManager
from langchain.schema import SystemMessage


class Generation:
    """
    Uses an LLM to generate the final answer for a Class 12 Physics question.
    
    For knowledge queries (that require retrieval), only the retrieved document context
    is provided (no chat history).
    
    For discussion queries, the chat history is passed along with the user query.
    """
    def __init__(self):
        self.knowledge_prompt_path = "system_prompts/knowledge.txt"
        self.discussion_prompt_path = "system_prompts/discussion.txt"
        self.chat_history_manager = ChatHistoryManager()

    def run(self, state: dict) -> dict:
        logging.info("Running generation node.")
        
        session_id = state.get("keys", {}).get("session_id", "")
        if not session_id:
            logging.error("No session ID provided.")
            return state

        question = state.get("keys", {}).get("question", "").strip()
        query_type = state.get("keys", {}).get("query_type", "knowledge")
        
        # Retrieve chat history for discussion queries
        chat_history = self.chat_history_manager.get_chat_history(session_id)
        chat_history_text = "\n".join([msg["content"] for msg in chat_history.get("messages", [])])
        
        # For knowledge queries, we use the retrieved document context and ignore chat history.
        if query_type == "knowledge":
            prompt_file = self.knowledge_prompt_path
            context = "\n\n".join([
                d.page_content if hasattr(d, "page_content") else d["page_content"]
                for d in state.get("keys", {}).get("documents", [])
            ])
            chat_context = ""  # Do not include chat history for knowledge queries.
        else:
            # For discussion queries, use chat history and no external context.
            prompt_file = self.discussion_prompt_path
            context = ""
            chat_context = chat_history_text

        # Load the appropriate prompt file.
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except Exception as e:
            logging.error(f"Error reading prompt template: {e}")
            prompt_template = ""

        # Build the prompt with the appropriate fields.
        prompt_tmpl = PromptTemplate(
            template=prompt_template,
            input_variables=["chat_history", "context", "user_query"]
        )
        # print(f"Prompt template: {prompt_tmpl}")
        prompt_str = prompt_tmpl.format(
            chat_history=chat_context,
            context=context,
            user_query=question
        )
        # print(f"Generation prompt:\n{prompt_str}")

        try:
            # result = llama_llm.invoke([SystemMessage(content=prompt_str)])
            response = client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp-01-21", contents=prompt_str
            )
            # print(response)
            generation_output = response.text
        except Exception as e:
            logging.error(f"Error during generation: {e}")
            generation_output = "Error generating answer."

        state.setdefault("keys", {})["generated_answer"] = generation_output
        return state
