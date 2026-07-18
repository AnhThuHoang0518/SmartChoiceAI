# -*- coding: utf-8 -*-
"""SPA fallback: deep-link /category/* phai tra index.html (khong 404) de
react-router tu dinh tuyen. API/chat/favicon van dung. Chan path traversal.

Bug that: mount StaticFiles(html=True) o '/' tra 404 cho /category/may-lanh ->
nut ngoanh nganh tren landing chet (vao thang/F5 ra {'detail':'Not Found'})."""
from fastapi.testclient import TestClient

from backend.app.main import app

c = TestClient(app)


def test_deep_link_category_tra_index_html_khong_404():
    for p in ("/category/may-lanh", "/category/tu-lanh", "/category/bat-ky"):
        r = c.get(p)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")
        assert "<!doctype html" in r.text.lower()


def test_api_va_chat_van_khong_bi_catch_all_nuot():
    assert c.get("/api/khuyen-mai").headers["content-type"].startswith("application/json")
    assert c.get("/healthz").json() == {"ok": True}
    assert "text/html" in c.get("/chat").headers.get("content-type", "")


def test_file_tinh_that_van_phuc_vu():
    r = c.get("/favicon.svg")
    assert r.status_code == 200 and "svg" in r.headers.get("content-type", "")


def test_chan_path_traversal():
    # khong duoc lo file ngoai dist -> tra ve index.html thay vi /etc/passwd
    r = c.get("/assets/../../../etc/passwd")
    assert "root:" not in r.text
    assert "<!doctype html" in r.text.lower()
