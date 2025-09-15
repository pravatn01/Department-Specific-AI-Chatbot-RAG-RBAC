import os
import shutil
from typing import List
from langchain_community.document_loaders import UnstructuredFileLoader, CSVLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# Paths & Settings
DATA_PATH = "../resources/data"
DB_PATH = "chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"

# Embedding model
embedding_fn = SentenceTransformerEmbeddings(model_name=MODEL_NAME)

# Helpers
def load_department_files(dept_folder: str) -> List:
    """Load all supported documents for a single department folder."""
    docs = []
    for fname in os.listdir(dept_folder):
        path = os.path.join(dept_folder, fname)
        try:
            if fname.endswith(".md"):
                try:
                    docs.extend(UnstructuredFileLoader(path).load())
                except:
                    docs.extend(TextLoader(path).load())
            elif fname.endswith(".csv"):
                docs.extend(CSVLoader(path).load())
        except Exception as err:
            print(f"❌ Skipped {fname}: {err}")
    return docs


def split_and_tag(docs: List, department: str) -> List:
    """Split into chunks and assign metadata for role/category."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    for d in split_docs:
        d.metadata = {
            "role": department.lower(),
            "category": "general" if department.lower() == "general" else department.lower()
        }
    return split_docs


def reset_chroma(path: str):
    """Delete existing Chroma database before persisting new one."""
    shutil.rmtree(path, ignore_errors=True)


# Main Pipeline
def build_vector_db():
    all_docs = []

    for dept in os.listdir(DATA_PATH):
        dept_dir = os.path.join(DATA_PATH, dept)
        if not os.path.isdir(dept_dir):
            continue

        print(f"\n🔎 Scanning department: {dept}")
        loaded = load_department_files(dept_dir)

        if not loaded:
            print(f"⚠️ No files found in {dept}")
            continue

        processed = split_and_tag(loaded, dept)
        all_docs.extend(processed)

        print(f"✅ {len(processed)} chunks prepared for {dept}")

    if not all_docs:
        print("\n❌ No documents processed. Aborting.")
        return

    reset_chroma(DB_PATH)
    db = Chroma.from_documents(
        documents=all_docs,
        embedding=embedding_fn,
        persist_directory=DB_PATH,
        collection_name="company_docs"
    )
    db.persist()

    print(f"\n🎉 Indexed {len(all_docs)} documents into Chroma.")
    print("Sample metadata:", db._collection.get()["metadatas"][:3])


# Entry Point
if __name__ == "__main__":
    build_vector_db()
