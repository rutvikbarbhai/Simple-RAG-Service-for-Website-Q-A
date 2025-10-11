# Simple RAG Service for Website Q&A

This project is a simple, self-contained Retrieval-Augmented Generation (RAG) service. Given a starting URL, it crawls a website, indexes its content, and answers questions strictly based on the information it has collected, providing citations for its answers.

---

## Architecture

The system follows a three-stage pipeline:

1.  **Crawl**: A `Scrapy` spider crawls a given domain, respecting `robots.txt` and staying within the domain scope. It extracts clean text from HTML pages and saves it to `data/url_to_doc.json`.
2.  **Index**: The text is loaded, split into overlapping chunks, and embedded into vectors using a `sentence-transformers` model. These vectors are stored in a local `ChromaDB` vector database for efficient retrieval.
3.  **Ask**: A user's question is embedded, and a similarity search retrieves the most relevant text chunks from ChromaDB. These chunks are passed as context to a local LLM (via `Ollama`) with a carefully engineered prompt that forces it to answer *only* from the provided text and refuse if the information is not present.

---

## Setup and Installation

**Prerequisites:**
* Python 3.9+
* [Ollama](https://ollama.com/) installed and running.

1.  **Clone the repository and create a virtual environment:**
    ```bash
    git clone <your-repo-url>
    cd rag-service
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Pull the LLM model using Ollama:**
    ```bash
    ollama pull llama3:8b-instruct
    ```

---

## How to Run

1.  **Start the API Server:**
    ```bash
    uvicorn src.api:app --reload
    ```
    The server will be available at `http://127.0.0.1:8000`.

2.  **Use the API Endpoints:**

    **a. Crawl a website:**
    ```bash
    curl -X POST "[http://127.0.0.1:8000/crawl](http://127.0.0.1:8000/crawl)" \
    -H "Content-Type: application/json" \
    -d '{"start_url": "[https://example.com](https://example.com)", "max_pages": 10}'
    ```

    **b. Index the crawled content:**
    ```bash
    curl -X POST "[http://127.0.0.1:8000/index](http://127.0.0.1:8000/index)"
    ```

    **c. Ask a question:**
    ```bash
    curl -X POST "[http://127.0.0.1:8000/ask](http://127.0.0.1:8000/ask)" \
    -H "Content-Type: application/json" \
    -d '{"question": "What is the main topic of this website?"}'
    ```

---

## Design and Tradeoffs

* **Crawler (`Scrapy`):** Chosen for its robustness, built-in politeness features (`ROBOTSTXT_OBEY`, `DOWNLOAD_DELAY`), and scalability.
* **Vector DB (`ChromaDB`):** Used for its simplicity and ease of local setup. For a larger-scale application, a more performant solution like FAISS or a managed service would be better.
* **Embedding Model (`all-MiniLM-L6-v2`):** A small, fast, and effective model that runs locally, perfect for this scale.
* **LLM (`Ollama` + `Llama 3`):** Provides powerful, local, and open-source generation capabilities. The key to success is the strict, grounded prompt.
* **Chunking (`800` chars, `100` overlap):** A balanced strategy to ensure context is preserved without creating chunks that are too broad.
