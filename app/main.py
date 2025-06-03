import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .utils import parse_resume, match

app = FastAPI()

# Mount the static folder so we can serve index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Return the simple HTML form in static/index.html.
    """
    html_path = os.path.join("static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    1) Read uploaded file bytes
    2) Derive plain text
    3) Compute top-5 matches
    4) Return list of {title, company, url}
    """
    # Only allow PDF or DOCX (or plaintext)
    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain"
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")

    raw = await file.read()
    text = parse_resume(raw, file.content_type)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from résumé.")

    results = match(text, topk=5)
    return {"matches": results}
