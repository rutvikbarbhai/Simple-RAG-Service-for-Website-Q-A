# filename: src/core/indexer.py

import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# --- Constants ---
CRAWLED_DATA_PATH = "data/url_to_doc.json"
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "website_content"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- ChromaDB Client Initialization ---
client = chromadb.PersistentClient(path=DB_PATH)

# Use SentenceTransformer for embeddings
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)

# Get or create the collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=sentence_transformer_ef,
    metadata={"hnsw:space": "cosine"} # Using cosine distance for similarity
)

# --- Core Functions ---

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Splits text into overlapping chunks."""
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i + size])
    return chunks

def run_indexing():
    """Loads crawled data, chunks it, and indexes into ChromaDB."""
    try:
        with open(CRAWLED_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Crawled data file not found at {CRAWLED_DATA_PATH}")
        return 0

    documents = []
    metadatas = []
    ids = []
    doc_id = 0

    print("Starting chunking and indexing process...")
    for url, content in data.items():
        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": url})
            ids.append(f"id_{doc_id}_{i}")
        doc_id += 1
    
    # Clear the collection before adding new data
    existing_ids = collection.get(include=[])['ids'] 
    if existing_ids:
     collection.delete(ids=existing_ids)
    
    # Add documents in batches to avoid overwhelming the system
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        print(f"Indexed batch {i//batch_size + 1}/{(len(documents)//batch_size)+1}")

    print(f"Indexing complete. Total vectors indexed: {len(documents)}")
    return len(documents)