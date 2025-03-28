from langchain_community.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from config import embeddings, ensemble_retriever_global, USE_PHYSICS_QA
from data_ingestion_pipeline import DocumentIngestionPipeline

ingestion_pipeline = DocumentIngestionPipeline()

def build_faiss_from_physics_qa(docs):
    db = FAISS.from_documents(docs, embeddings)
    db.save_local("faiss_class12_physics_index")
    return db


def load_ensemble_retriever():
    global ensemble_retriever_global
    if USE_PHYSICS_QA:
        csv_file = "class12_physics_qa.csv"  # Adjust the path as needed
        docs = ingestion_pipeline.load_class12_physics_qa_csv(csv_file)
        if Path("faiss_class12_physics_index").exists():
            db = FAISS.load_local("faiss_class12_physics_index", embeddings, allow_dangerous_deserialization=True)
        else:
            db = build_faiss_from_physics_qa(docs)
        vectorstore_retriever = db.as_retriever(search_kwargs={"k": 3})
        keyword_retriever = BM25Retriever.from_documents(docs)
        ensemble_retriever_global = EnsembleRetriever(
            retrievers=[vectorstore_retriever, keyword_retriever],
            weights=[0.5, 0.5]
        )
    else:
        # Fallback to another ingestion method if needed
        pass
    print("EnsembleRetriever is ready.")
    return ensemble_retriever_global
