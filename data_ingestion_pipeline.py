import csv
from typing import List
from langchain.docstore.document import Document

class DocumentIngestionPipeline:
    def __init__(self):
        # If you already have other pipeline init code, keep it here
        pass

    def load_class12_physics_qa_csv(self, csv_file: str) -> List[Document]:
        """
        Loads a CSV of Class 12 Physics Q&A. The CSV should have two columns:
          - Question
          - Solution
        Returns a list of LangChain Document objects, each with:
          - page_content = "Question: <question>\\nSolution: <solution>"
          - metadata = { "question": <question> }
        """
        docs = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # expects columns: Question, Solution
            for row in reader:
                question = row["Question"].strip()
                solution = row["Solution"].strip()

                # Combine question & solution in the doc’s text
                content = f"Question: {question}\nSolution: {solution}"

                # Create a Document with both Q & A in the page_content
                doc = Document(
                    page_content=content,
                    metadata={"question": question}
                )
                docs.append(doc)

        return docs
