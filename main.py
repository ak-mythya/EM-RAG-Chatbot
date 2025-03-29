from graph_assembly import app
from chat_history_manager import ChatHistoryManager

'''def run_physics_qa_pipeline(question: str, session_id: str) -> str:
    # Create the initial state for the pipeline.
    inputs = {"keys": {"question": question, "session_id": session_id}}
    final_answer = "No final generation produced."
    
    # Stream the state through the LangGraph pipeline.
    for output in app.stream(inputs):
        for step_name, step_data in output.items():
            # Expect the final node to store the final answer in "generated_answer"
            final_answer = step_data["keys"].get("generated_answer", final_answer)
    
    return final_answer'''


import re
import json

def run_physics_qa_pipeline(question: str, session_id: str) -> str:
    # Create the initial state for the pipeline.
    inputs = {"keys": {"question": question, "session_id": session_id}}
    final_answer = "No final generation produced."
    json_found = False  # Flag to track if valid JSON has been found

    # Stream the state through the LangGraph pipeline.
    for output in app.stream(inputs):
        for step_name, step_data in output.items():
            # Expect the final node to store the final answer in "generated_answer"
            generated_answer = step_data["keys"].get("generated_answer")
            print(f"Step: {step_name}, Generated Answer: {generated_answer}")  # Debugging

            print(f"Before if: step_name={step_name}, generated_answer={generated_answer}, json_found={json_found}")  # Debugging

            if step_name == "generate" and generated_answer and not json_found:
                print("Inside if condition")  # Debugging
                if isinstance(generated_answer, str) and generated_answer.strip():
                    # Remove markdown code fences and any control characters (e.g., newline, carriage return) using regex
                    json_string = generated_answer.replace("```json", "").replace("```", "")
                    json_string = re.sub(r"[\x00-\x1F]+", " ", json_string).strip()
                    try:
                        data = json.loads(json_string)
                        final_answer = data.get("final_response", "No final response found in JSON.")
                        json_found = True
                        print(f"Successfully parsed JSON. Final Answer: {final_answer}")  # Debugging
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        final_answer = "Error: Could not decode JSON response."
                    except KeyError:
                        print("Error: 'final_response' key not found in JSON.")
                        final_answer = "Error: 'final_response' key not found."
                else:
                    print("Generated answer is empty or not a string, skipping.")
            elif not generated_answer and not json_found:
                print("No generated_answer found in step_data, skipping.")
            else:
                print("Skipping due to other conditions")  # Debugging

    print("Final Answer_1:", final_answer)  # Debugging
    return final_answer

def main():
    # Example query from a Class 12 Physics student.
    user_question = ("A satellite is moving very close to a planet of density 𝜌 ρ. The time period of the satellite isMagnitude of potential energy ( 𝑈 U) and time period ( 𝑇 T) of a satellite are related to each other as:")
    #user_question = ("Since halving the distance between the Earth and the Sun reduces the orbital period to about 129 days, how would that affect the gravitational force between them and what implications would it have for the Earth's orbital speed?")
    session_id = "session_001"  # This could be dynamically generated or provided by your web framework.
    
    answer = run_physics_qa_pipeline(user_question, session_id)
    print("Final Answer:\n", answer)
    
    # Update chat history after processing the query.
    chat_history_manager = ChatHistoryManager("chat_history.json")
    chat_history_manager.update_chat_history(session_id, user_question, answer)

if __name__ == "__main__":

    main()
