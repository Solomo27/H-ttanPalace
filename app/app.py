from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=BASE_DIR/"templates")

app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

@app.get("/")
def get_landing_page(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "user": None}
    )