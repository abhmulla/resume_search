# utils.py
import re
import json
import os
import tempfile
import numpy as np
import faiss
import docx2txt
from sentence_transformers import SentenceTransformer
from pdfminer.high_level import extract_text  # Direct PDF text extraction

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
JOBS_PATH = os.path.join(os.path.dirname(__file__), "jobs.json")  # Corrected path

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading jobs from jobs.json...")
try:
    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)
except FileNotFoundError:
    print(f"Error: {JOBS_PATH} not found. Run scripts/fetch_jobs.py first.")
    jobs = []

# Only compute embeddings if jobs exist
if jobs:
    print("Computing job embeddings...")
    job_texts = [j["title"] + " " + j["description"] for j in jobs]
    job_embs = model.encode(job_texts, convert_to_numpy=True, show_progress_bar=True)
    
    dim = job_embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(job_embs)
    index.add(job_embs)
    print(f"FAISS index built with {index.ntotal} vectors (dim={dim}).")
else:
    index = None
    print("Warning: No jobs loaded. Index not created.")

def parse_resume(file_bytes: bytes, mime: str) -> str:
    """Extract text from resume files safely"""
    try:
        if mime == "application/pdf":
            # Use PDF miner directly
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            
            try:
                return extract_text(tmp_path)
            finally:
                os.unlink(tmp_path)  # Clean up temp file
                
        elif mime in (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
                
            try:
                return docx2txt.process(tmp_path)
            finally:
                os.unlink(tmp_path)
                
        else:  # Plain text
            return file_bytes.decode("utf-8", errors="ignore")
            
    except Exception as e:
        print(f"Error processing file: {e}")
        return ""

def match(resume_text: str, topk: int = 5):
    """Find matching jobs with safety checks"""
    if not resume_text or not index:
        return []
    
    q_emb = model.encode([resume_text], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, topk)
    
    return [{
        "title": jobs[i]["title"],
        "company": jobs[i]["company_name"],
        "url": jobs[i]["url"]
    } for i in I[0] if i < len(jobs)]