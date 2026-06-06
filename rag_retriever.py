import os
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Dependencies check to guide you/your teammate during setup:
# pip install langchain-chroma langchain-community unstructured[pdf] sentence-transformers

DB_DIR = os.path.join(os.getcwd(), "chroma_db")
DATA_DIR = os.path.join(os.getcwd(), "data")

@st.cache_resource
def get_embeddings_engine():
    """Loads and caches the local BGE embedding model weights onto CPU."""
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={'normalize_embeddings': True}
    )

def build_or_load_vector_db():
    """
    Ingests all files inside the /data directory using Unstructured,
    chunks them, embeds them with BGE, and saves/loads a persistent ChromaDB instance.
    """
    embeddings = get_embeddings_engine()
    
    # Ensure our source data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # If ChromaDB already exists on disk, load it instantly instead of rebuilding
    if os.path.exists(DB_DIR) and len(os.listdir(DB_DIR)) > 0:
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
        
    # Otherwise, parse data folder files using Unstructured Partitioning
    from langchain_community.document_loaders import UnstructuredFileLoader
    
    supported_extensions = (".txt", ".pdf", ".docx", ".md")
    all_docs = []
    
    if not os.path.exists(DATA_DIR):
        return None
        
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(supported_extensions)]
    
    if not files:
        # Return None or empty database safely if no files are placed in /data yet
        return None

    for file_name in files:
        file_path = os.path.join(DATA_DIR, file_name)
        try:
            # Unstructured handles complex document parsing patterns automatically
            loader = UnstructuredFileLoader(file_path)
            loaded_documents = loader.load()
            for d in loaded_documents:
                d.metadata["source"] = file_name  # Ensure source name tracker matches contract
            all_docs.extend(loaded_documents)
        except Exception as e:
            print(f"Skipping corrupt or unreadable file {file_name}: {e}")

    if not all_docs:
        return None

    # Segment documents with a tight sliding window constraint
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_docs)

    # Compile vectors directly down into your local ChromaDB directory
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    return vector_db


def retrieve_enterprise_docs(query: str) -> dict:
    """
    CONTRACT 1 FUNCTION:
    Accepts: A raw user query string.
    Returns: A dictionary with a compiled string context block and a list of file sources.
    """
    # 1. Initialize or connect to the persistent ChromaDB matrix
    vector_db = build_or_load_vector_db()
    
    # Fallback response structure if database is empty or data folder hasn't been populated yet
    if vector_db is None:
        return {
            "context": "System notice: No source files found in the backend server storage directory.",
            "sources": ["No Documents Loaded"]
        }
        
    # 2. Query ChromaDB for the top 2 closest mathematical matches (k=2)
    matched_chunks = vector_db.similarity_search(query, k=2)
    
    # 3. Format the context block and extract unique metadata document sources
    context_string = "\n\n".join([chunk.page_content for chunk in matched_chunks])
    sources_list = list(set([chunk.metadata.get("source", "Unknown File") for chunk in matched_chunks]))
    
    return {
        "context": context_string,
        "sources": sources_list
    }