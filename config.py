from langchain_google_genai import ChatGoogleGenerativeAI
import os

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyB8QjzwpuK2z1-RkzCPJux1J11_QSLYZy8"
llama_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-thinking-exp-01-21",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
ensemble_retriever_global = None
USE_PHYSICS_QA = True

from google import genai

client = genai.Client(api_key="AIzaSyB8QjzwpuK2z1-RkzCPJux1J11_QSLYZy8")