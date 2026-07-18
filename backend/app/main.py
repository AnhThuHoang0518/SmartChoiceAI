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

# Trang chat tach khoi frontend/public: public la thu muc "public" cua vite
# (anh landing) - de chat index.html o do se dung do voi index.html vite build.
GIAO_DIEN = Path("frontend/chat")        # trang chat (HTML thuan, 1 file)
LANDING = Path("frontend/dist")          # landing React da build (vite build)


@app.get("/healthz")
def healthz():
    return {"ok": True}


if GIAO_DIEN.exists():
    app.mount("/static", StaticFiles(directory=GIAO_DIEN), name="static")

    @app.get("/chat")
    def trang_chat():
        return FileResponse(GIAO_DIEN / "index.html")

    if LANDING.exists():
        # Landing React o goc "/", chat o "/chat". Mount "/" dat CUOI de cac
        # route API/healthz/chat khai bao truoc van thang.
        app.mount("/", StaticFiles(directory=LANDING, html=True), name="landing")
    else:
        # Chua build landing (dev local chua chay npm) -> "/" van la chat,
        # khong co gi bi 404.
        @app.get("/")
        def trang_chu():
            return FileResponse(GIAO_DIEN / "index.html")
