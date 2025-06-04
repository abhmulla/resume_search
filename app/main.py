# main.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from .utils import parse_resume, match

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the frontend"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "index.html"))

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Process uploaded resumes"""
    valid_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain"
    }
    
    if file.content_type not in valid_types:
        raise HTTPException(400, "Unsupported file type. Use PDF, DOCX or TXT.")

    try:
        raw = await file.read()
        text = parse_resume(raw, file.content_type)
        if not text.strip():
            raise HTTPException(400, "Extracted text is empty")
            
        return {"matches": match(text, 5)}
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")