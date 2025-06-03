# utils.py
import re
import json
import numpy as np
import spacy
import faiss
from pyresparser import ResumeParser
import pyresparser.resume_parser
import docx2txt
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
JOBS_PATH  = "app/jobs.json"

spacy_model = spacy.load("en_core_web_sm")

# ----- 1) Load model and index as globals on import -----
print("Loading embedding model…")
model = SentenceTransformer(MODEL_NAME)

print("Loading jobs from jobs.json…")
with open(JOBS_PATH, "r", encoding="utf-8") as f:
    jobs = json.load(f)

# Precompute embeddings for each job title+description
print("Computing job embeddings (this may take ~20 s)…")
job_texts = [j["title"] + " " + j["description"] for j in jobs]
job_embs = model.encode(job_texts, convert_to_numpy=True, show_progress_bar=True)

# Build a flat (inner product) FAISS index on those embeddings
dim = job_embs.shape[1]
index = faiss.IndexFlatIP(dim)  # cosine similarity (after normalizing)
faiss.normalize_L2(job_embs)    # normalize embeddings to unit length
index.add(job_embs)
print(f"FAISS index built with {index.ntotal} vectors (dim={dim}).")

def parse_resume(file_bytes: bytes, mime: str) -> str:
    """
    1) If PDF, let pyresparser extract text.
    2) Otherwise, if docx, use docx2txt.
    3) Normalize whitespace.
    """
    text = ""
    if mime == "application/pdf":
        with open("temp_resume.pdf", "wb") as tmp:
            tmp.write(file_bytes)
        # Monkey patch spaCy load globally before ResumeParser uses it
        original_spacy_load = spacy.load
        spacy.load = lambda name="en_core_web_sm": spacy_model
        try:
            data = ResumeParser("temp_resume.pdf").get_extracted_data()
            text = data.get("text", "") or ""
        finally:
            spacy.load = original_spacy_load  #Restore
    elif mime in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ):
        with open("temp_resume.docx", "wb") as tmp:
            tmp.write(file_bytes)
        text = docx2txt.process("temp_resume.docx")
    else:
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except:
            text = ""

    return re.sub(r"\s+", " ", text).strip()


def match(resume_text: str, topk: int = 5):
    """
    1) Embed the resume
    2) Normalize
    3) Search FAISS
    4) Return topk job dicts
    """
    if not resume_text:
        return []
    q_emb = model.encode(resume_text, convert_to_numpy=True)
    faiss.normalize_L2(q_emb.reshape(1, -1))
    D, I = index.search(q_emb.reshape(1, -1), topk)
    results = []
    for idx in I[0]:
        job = jobs[idx]
        results.append({
            "title": job["title"],
            "company": job["company_name"],
            "url": job["url"]
        })
    return results
