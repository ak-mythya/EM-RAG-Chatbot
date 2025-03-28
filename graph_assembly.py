from langgraph.graph import END, StateGraph
from typing import TypedDict, Dict

# Import your nodes for the Class 12 Physics QA pipeline.
# Ensure these nodes are configured to work with your QA dataset.
from node_retrieval import SimpleRetriever
from node_genertion import Generation
from node_classifier import QueryClassifier

# Define the graph state type.
class GraphState(TypedDict):
    keys: Dict[str, any]

# Initialize the state graph.
workflow = StateGraph(GraphState)

# Instantiate nodes.
# The ContextAwareRetriever should be configured in retriever_setup.py to load
# the FAISS/BM25 index built from your Class 12 Physics Q&A CSV.
classifier = QueryClassifier()
retriever = SimpleRetriever()
# Generation node uses a prompt (e.g., system_prompts/in-scope_physics.txt)
generation = Generation()

# Register nodes in the graph.
workflow.add_node("classify_query", classifier.run)
workflow.add_node("retrieve", retriever.run)
workflow.add_node("generate", generation.run)

# Define graph routing.
# Here we treat the entire user query as the only query (no sub-query identification).
# Set the entry point.
workflow.set_entry_point("classify_query")

# Conditional edge based on query type.
workflow.add_conditional_edges(
    "classify_query",
    lambda state: state.get("keys", {}).get("query_type", "knowledge"),
    {
        "knowledge": "retrieve",
        "discussion": "generate"
    }
)
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile the graph.
app = workflow.compile()
