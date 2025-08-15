from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import os

API_BASE = os.environ.get("API_BASE", "http://api:5001")

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    languages = []
    error = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_BASE}/languages")
            resp.raise_for_status()
            languages = resp.json().get("languages", [])
    except Exception as e:
        error = f"Could not load languages: {e}"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "languages": languages,
        "original_text": "",
        "translated_text": "",
        "detected_language": None,
        "pronunciation": None,
        "src_lang": "auto",
        "dest_lang": "es",
        "include_pronunciation": False,
        "error": error
    })

@app.post("/", response_class=HTMLResponse)
async def form_post(
    request: Request,
    text: str = Form(...),
    src: str = Form("auto"),
    dest: str = Form("es"),
    pronunciation: str = Form(None)
):
    languages = []
    error = None
    detected_language = None
    translated_text = ""
    original_text = text
    pronunciation_val = pronunciation is not None
    pronunciation_result = None
    try:
        async with httpx.AsyncClient() as client:
            lang_resp = await client.get(f"{API_BASE}/languages")
            lang_resp.raise_for_status()
            languages = lang_resp.json().get("languages", [])
            payload = {
                "text": text,
                "src": src,
                "dest": dest,
                "pronunciation": pronunciation_val
            }
            resp = await client.post(f"{API_BASE}/translate", json=payload)
            data = resp.json()
            if resp.status_code == 200:
                translated_text = data.get("translated_text", "")
                detected_language = data.get("detected_language")
                pronunciation_result = data.get("pronunciation")
            else:
                error = data.get("error", "Translation failed")
    except Exception as e:
        error = f"Translation failed: {e}"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "languages": languages,
        "original_text": original_text,
        "translated_text": translated_text,
        "detected_language": detected_language,
        "pronunciation": pronunciation_result,
        "src_lang": src,
        "dest_lang": dest,
        "include_pronunciation": pronunciation_val,
        "error": error
    })
