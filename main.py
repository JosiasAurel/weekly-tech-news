from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from news import get_recent_week_entries

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    articles = get_recent_week_entries()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles})

# Optional: run the server if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)