import logging
from typing import List, Dict
from retriever_setup import load_ensemble_retriever
from config import llama_llm

class SimpleRetriever:
    """
    Retrieves documents for a given query using the ensemble retriever.
    This node performs simple retrieval without checking cached context.
    """
    def __init__(self):
        self.ensemble_retriever = load_ensemble_retriever()

    def run(self, state: dict) -> dict:
        logging.info("Running simple retrieval node for Physics QA.")
        
        # Get the user question from the state
        question = state.get("keys", {}).get("question", "").strip()
        if not question:
            logging.error("No question provided for retrieval.")
            state.setdefault("keys", {})["documents"] = []
            return state

        try:
            # Configure retrieval parameters (e.g., top_k = 8)
            config = {"search_kwargs_faiss": {"k": 8}}
            retrieved_docs = self.ensemble_retriever.invoke(question, config=config)
            docs = list(retrieved_docs)
        except Exception as e:
            logging.error(f"Error during retrieval: {e}")
            docs = []

        # Update the state with retrieved documents
        state.setdefault("keys", {})["documents"] = docs
        return state
