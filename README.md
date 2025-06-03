# Resume → Job Matcher (Mini-Prototype)

This repo demonstrates a quick “upload résumé → semantic job match” flow using:
- FastAPI  
- pyresparser / python-docx  
- Sentence-Transformers (MiniLM)  
- FAISS (flat, inner-product index)  
- Remotive job API  

---

1. **Clone repo**  
2. **Set up & activate** a virtual environment  
3. **Install** prerequisites (`pip install -r requirements.txt`)  
4. **Fetch job postings** (`python scripts/fetch_jobs.py`)  
5. **Launch FastAPI** (`uvicorn app.main:app --reload`)  
6. **Open** `http://127.0.0.1:8000/` in your browser and upload any PDF/DOCX résumé  
