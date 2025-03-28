from graph_assembly import app
from chat_history_manager import ChatHistoryManager

def run_physics_qa_pipeline(question: str, session_id: str) -> str:
    # Create the initial state for the pipeline.
    inputs = {"keys": {"question": question, "session_id": session_id}}
    final_answer = "No final generation produced."
    
    # Stream the state through the LangGraph pipeline.
    for output in app.stream(inputs):
        for step_name, step_data in output.items():
            # Expect the final node to store the final answer in "generated_answer"
            final_answer = step_data["keys"].get("generated_answer", final_answer)
    
    return final_answer

def main():
    # Example query from a Class 12 Physics student.
    user_question = ("Since halving the distance between the Earth and the Sun reduces the orbital period to about 129 days, how would that affect the gravitational force between them and what implications would it have for the Earth's orbital speed?")
    session_id = "session_001"  # This could be dynamically generated or provided by your web framework.
    
    answer = run_physics_qa_pipeline(user_question, session_id)
    print("Final Answer:\n", answer)
    
    # Update chat history after processing the query.
    chat_history_manager = ChatHistoryManager("chat_history.json")
    chat_history_manager.update_chat_history(session_id, user_question, answer)

if __name__ == "__main__":
    main()
