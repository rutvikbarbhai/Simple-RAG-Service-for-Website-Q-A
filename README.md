# <img src="https://github.com/user-attachments/assets/ed86026d-6c9d-4fc3-b324-b58defa239de" width="45px"> Simple RAG Service for Website Q&A
This project is a simple, self-contained Retrieval-Augmented Generation (RAG) service. Given a starting URL, it crawls a website, indexes its content, and answers questions strictly based on the information it has collected, providing citations for its answers.

---
## <img src="https://github.com/user-attachments/assets/f3dcee8e-e008-457a-97fb-d3848b425713" height="30px" style="vertical-align:text-bottom;"> Repository Contents

```bash
📁 rag-service/
├── 📁 data/  # Croma DB
│   ├── 📁 2ae9c630-c5e6-4e30-b218-28405640909a/
│   │   ├── data_level0.bin
│   │   ├── header.bin
│   │   ├── length.bin
│   │   └── link_lists.bin
│   ├── chroma.sqlite3
│   └── url_to_doc.json
├── 📁 src/
│   ├── 📁 __pycache__/
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── indexer.py
│   │   ├── qa.py
│   │   └── __pycache__/
│   └── 📁 crawler/
│       └── 📁 crawler/
│           └── 📁 spiders/
│               └── site_spider.py
└── 📄 README.md

```
## <img src="https://github.com/user-attachments/assets/c867040d-ee55-406b-959b-332d3d9997b1" height="25px" style="vertical-align: middle; margin-right: 5px;"> Architecture
<img width="761" height="360" alt="image" src="https://github.com/user-attachments/assets/b552a692-091d-441d-bc71-ccb3fae66a0d" />

The system follows a three-stage pipeline:

1️⃣.  **Crawl**: A `Scrapy` spider crawls a given domain, respecting `robots.txt` and staying within the domain scope. It extracts clean text from HTML pages and saves it to `data/url_to_doc.json`.

2️⃣.  **Index**: The text is loaded, split into overlapping chunks, and embedded into vectors using a `sentence-transformers` model. These vectors are stored in a local `ChromaDB` vector database for efficient retrieval.

3️⃣.  **Ask**: A user's question is embedded, and a similarity search retrieves the most relevant text chunks from ChromaDB. These chunks are passed as context to a local LLM (via `Ollama`) with a carefully engineered prompt that forces it to answer *only* from the provided text and refuse if the information is not present.



## <img src="https://github.com/user-attachments/assets/6672ee8c-15ed-4fb5-9cd5-63c04ac747c1" height="24px" style="vertical-align:bottom;">  Setup and Installation

## <img src="https://github.com/user-attachments/assets/dcdcffb4-c4e2-40ee-84cc-aca8612d257e" height="30px" style="vertical-align: text-bottom; margin-bottom:-3050px;"> Prerequisites:
* Python 3.9+
* [Ollama](https://ollama.com/) installed and running.

### 1️⃣. Clone the Repository & create your virtual enviroment

    git clone <your-repo-url>
    cd rag-service
    python -m venv venv
    source venv/bin/activate


### 2️⃣. Install Dependencies
    
    pip install -r requirements.txt


### 3️⃣. Pull the LLM model using Ollama:

    ollama pull llama3:8b-instruct


---

## How to Run

### 1️⃣. Start the API Server:

    uvicorn src.api:app --reload
    The server will be available at `http://127.0.0.1:8000`.

### 2️⃣. Use the API Endpoints:

### a. Crawl a website:
    
    curl -X POST "[http://127.0.0.1:8000/crawl](http://127.0.0.1:8000/crawl)" \
    -H "Content-Type: application/json" \
    -d '{"start_url": "[https://example.com](https://example.com)", "max_pages": 10}'
    

### b. Index the crawled content:
   
    curl -X POST "[http://127.0.0.1:8000/index](http://127.0.0.1:8000/index)"
    

### c. Ask a question:
    
    curl -X POST "[http://127.0.0.1:8000/ask](http://127.0.0.1:8000/ask)" \
    -H "Content-Type: application/json" \
    -d '{"question": "What is the main topic of this website?"}'
    

---

## <img src="https://github.com/user-attachments/assets/612137fd-b2de-411c-acd7-f94c4811e9f2" height="25px" style="vertical-align:text-bottom;"> Design and Tradeoffs

* **Crawler (`Scrapy`):** Chosen for its robustness, built-in politeness features (`ROBOTSTXT_OBEY`, `DOWNLOAD_DELAY`), and scalability.
* **Vector DB (`ChromaDB`):** Used for its simplicity and ease of local setup. For a larger-scale application, a more performant solution like FAISS or a managed service would be better.
* **Embedding Model (`all-MiniLM-L6-v2`):** A small, fast, and effective model that runs locally, perfect for this scale.
* **LLM (`Ollama` + `Llama 3`):** Provides powerful, local, and open-source generation capabilities. The key to success is the strict, grounded prompt.
* **Chunking (`800` chars, `100` overlap):** A balanced strategy to ensure context is preserved without creating chunks that are too broad.
