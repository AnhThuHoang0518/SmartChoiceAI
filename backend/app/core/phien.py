# -*- coding: utf-8 -*-
"""May trang thai hoi thoai - giu o nhu cau PHIA SERVER.

Vi sao khong de trong lich su chat cho LLM tu nho: da tra gia mot lan o du an
truoc (AI Butler) - de LLM tu slot-filling qua lich su thi no TROI FLOW: hoi
lan man, quen mat nhu cau ban dau, luot sau lat nguoc thong tin luot truoc.
Phai da xoa di lam lai bang may trang thai.

O day o nhu cau la mot object Pydantic o server. LLM khong bao gio duoc ghi de
truc tiep - moi thay doi phai qua ham gop, va o da biet thi khong bi ghi de.
"""
from __future__ import annotations

import time
import uuid

from backend.app.schemas.nhu_cau import ONhuCauMayLanh

# Bo nho trong RAM: du cho demo/hackathon. Len that thi thay bang Redis, doi
# dung mot cho nay - phan con lai khong biet gi ve noi luu.
_KHO: dict[str, dict] = {}
HAN_GIAY = 60 * 60


def tao_phien() -> str:
    ma = uuid.uuid4().hex[:12]
    _KHO[ma] = {"nhu_cau": ONhuCauMayLanh(), "luc": time.time(), "so_luot": 0,
                "da_hoi": []}
    return ma


def lay(ma: str) -> dict | None:
    p = _KHO.get(ma)
    if not p:
        return None
    if time.time() - p["luc"] > HAN_GIAY:
        _KHO.pop(ma, None)
        return None
    return p


def ghi(ma: str, nhu_cau: ONhuCauMayLanh, o_vua_hoi: str | None = None) -> None:
    p = _KHO.setdefault(ma, {"nhu_cau": ONhuCauMayLanh(), "so_luot": 0, "da_hoi": []})
    p["nhu_cau"] = nhu_cau
    p["luc"] = time.time()
    p["so_luot"] += 1
    if o_vua_hoi:
        p["da_hoi"].append(o_vua_hoi)


def don_het() -> None:
    _KHO.clear()
