from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from news import get_recent_week_entries, get_and_write_news
import os

SQLITE_DB_PATH = "./tops.db"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    articles = get_recent_week_entries()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles})

@app.get("/update-news")
async def health_check(request: Request):
    get_and_write_news()
    return {"status": "ok", "message": "News entries updated successfully"}


@app.get("/download-db")
def download_db():
    return FileResponse(
        path=SQLITE_DB_PATH,
        media_type='application/octet-stream',
        filename=os.path.basename(SQLITE_DB_PATH)
    )
