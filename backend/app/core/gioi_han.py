# -*- coding: utf-8 -*-
"""Chan spam goi API - rate limit theo IP, luu trong RAM.

Vi sao khong dung thu vien ngoai (slowapi...): demo chay 1 tien trinh tren
1 VPS (khong scale ngang), giong dung cach _KHO cua backend/app/core/phien.py
cho don gian, khong them dependency. Len that/scale ngang thi thay bang Redis
INCR + EXPIRE - cho nay la diem duy nhat can doi.

Uu tien doc IP that qua header X-Forwarded-For vi Caddy dung lam reverse
proxy (xem AGENTS.md, muc Deploy & ha tang) - neu doc thang request.client.host
thi moi request se ra IP noi bo cua Caddy, rate limit theo IP se VO NGHIA.
"""
from __future__ import annotations

import os
import time

from starlette.requests import Request

# {ip: [timestamp, ...]} - moi endpoint 1 "khoang" rieng (chat/anh/doc khac
# muc do ton tien khac nhau nen gioi han khac nhau).
_GOI: dict[str, dict[str, list[float]]] = {}


def _dang_test() -> bool:
    """Bo qua gioi han khi: (a) chay duoi pytest (bien PYTEST_CURRENT_TEST do
    chinh pytest tu dat, khong can cau hinh gi), hoac (b) script danh gia
    hang loat tu bat SMARTCHOICE_TAT_GIOI_HAN=1. Ca hai deu goi tu MOT "IP" gia
    (TestClient) hang tram lan/giay - nhieu hon bat ky khach that nao - nen
    khong the dung chung nguong voi luong khach that."""
    return bool(os.getenv("PYTEST_CURRENT_TEST")) or os.getenv(
        "SMARTCHOICE_TAT_GIOI_HAN") == "1"


def lay_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "khong-ro-ip"


def qua_gioi_han(request: Request | None, khoang: str, so_lan_toi_da: int,
                  cua_so_giay: float = 60.0) -> bool:
    """True neu IP nay da goi >= so_lan_toi_da lan trong cua_so_giay giay gan
    nhat cho 'khoang' (ten endpoint). Ghi nhan luon lan goi hien tai neu con
    duoi han (khong can goi ham khac de "dung" lan goi).

    request=None (goi ham chat()/nhin_anh_khach()/doc_thanh_tieng() truc tiep
    tu unit test, khong qua HTTP that) -> khong co IP that de gioi han, bo qua."""
    if request is None or _dang_test():
        return False
    ip = lay_ip(request)
    bay_gio = time.time()
    theo_khoang = _GOI.setdefault(khoang, {})
    ds = theo_khoang.setdefault(ip, [])
    ds[:] = [t for t in ds if bay_gio - t < cua_so_giay]      # don qua han
    if len(ds) >= so_lan_toi_da:
        return True
    ds.append(bay_gio)

    # Don rac ngau nhien de _GOI khong phinh vo han (demo dai ngay khong restart).
    if len(theo_khoang) > 5000:
        for k in list(theo_khoang):
            theo_khoang[k] = [t for t in theo_khoang[k] if bay_gio - t < cua_so_giay]
            if not theo_khoang[k]:
                theo_khoang.pop(k, None)
    return False
