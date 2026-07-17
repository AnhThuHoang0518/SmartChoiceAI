# -*- coding: utf-8 -*-
"""Smart Choice - tro ly AI so sanh va tu van san pham theo nhu cau that.

Chay:  uvicorn backend.app.main:app --reload --port 8000
"""
from dotenv import load_dotenv

load_dotenv()          # doc .env TRUOC khi bat cu module nao dong toi LLM

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.api.chat import router

app = FastAPI(title="Smart Choice", version="0.1.0")
app.include_router(router, prefix="/api")

GIAO_DIEN = Path("frontend/public")


@app.get("/healthz")
def healthz():
    return {"ok": True}


if GIAO_DIEN.exists():
    app.mount("/static", StaticFiles(directory=GIAO_DIEN), name="static")

    @app.get("/")
    def trang_chu():
        return FileResponse(GIAO_DIEN / "index.html")
