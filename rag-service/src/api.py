# filename: src/api.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import subprocess
import time

from src.core.indexer import run_indexing
from src.core.qa import answer_question

app = FastAPI(
    title="Simple RAG Service",
    description="An API for crawling, indexing, and asking questions to a website."
)

# --- Pydantic Models for Request/Response ---

class CrawlRequest(BaseModel):
    start_url: str
    max_pages: int = 30

class CrawlResponse(BaseModel):
    status: str
    message: str

class IndexResponse(BaseModel):
    status: str
    vector_count: int

class AskRequest(BaseModel):
    question: str
    top_k: int = 5

class Source(BaseModel):
    url: str
    snippet: str

class Timings(BaseModel):
    retrieval_ms: int
    generation_ms: int
    total_ms: int

class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    timings: Timings

# --- API Endpoints ---

@app.post("/crawl", response_model=CrawlResponse)
def crawl_endpoint(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Starts a background task to crawl a website.
    """
    def crawl_task():
        print(f"Starting crawl for {request.start_url}")
        command = [
            "scrapy", "runspider", "src/crawler/crawler/spiders/site_spider.py",
            "-a", f"start_url={request.start_url}",
            "-a", f"max_pages={request.max_pages}"
        ]
        subprocess.run(command, check=True)
        print("Crawl finished.")

    background_tasks.add_task(crawl_task)
    return {"status": "success", "message": f"Crawling started for {request.start_url}. This will run in the background."}


@app.post("/index", response_model=IndexResponse)
def index_endpoint():
    """
    Indexes the content crawled from the website.
    """
    try:
        vector_count = run_indexing()
        return {"status": "success", "vector_count": vector_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    """
    Asks a question and gets an answer grounded in the indexed content.
    """
    total_start_time = time.time()
    try:
        result = answer_question(request.question, request.top_k)
        total_end_time = time.time()

        # Add total time to timings
        total_ms = round((total_end_time - total_start_time) * 1000)
        result["timings"]["total_ms"] = total_ms

        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "RAG Service is running. Visit /docs for API documentation."}