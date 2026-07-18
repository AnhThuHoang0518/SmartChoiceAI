# -*- coding: utf-8 -*-
"""Ban cau QUAI vao /api/chat de san bug truoc gio cham.

Chay:  python scripts/thu_cau_quai.py

Chi khoa 2 dieu bat bien voi MOI dau vao, ke ca dau vao ac y:
  1. Khong bao gio 500 (loi server lo ra khach)
  2. Khong bao gio tra text rong (khach nhin man hinh trang)
Ket cuc CU THE (tu van hay tu choi) khong cham o day - bo 62 tinh huong lo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("LLM_NHA_CUNG_CAP", "luat")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402

CAU_QUAI = [
    "",                                        # rong
    "   ",                                     # toan khoang trang
    "🔥🔥🔥",                                   # chi emoji
    "5",                                       # chi mot so
    "<script>alert(1)</script> máy lạnh 15tr", # XSS thu
    "máy lạnh " + "rẻ " * 250,                 # cau sieu dai
    "may\nlanh\n18m2\n15tr",                   # xuong dong giua chung
    "I need an air conditioner for my room",   # tieng Anh
    "máy lạnh 0 đồng",                         # ngan sach 0
    "máy lạnh 500k phòng 18m2",                # ngan sach phi ly
    "máy lạnh phòng 1000m2",                   # phong phi ly
    "tủ lạnh cho nhà 0 người",                 # so nguoi 0
    "tủ lạnh nhà 99 người",                    # so nguoi phi ly
    "máy lạnh -5 triệu",                       # so am
    "mua máy lạnh và tủ lạnh và máy giặt",     # 3 nganh 1 cau
    "so sánh máy 1 và máy 2",                  # so sanh khi CHUA co bang
    "so sánh máy 7 và máy 9",                  # chi so ngoai pham vi
    "máy lạnh 18m2 15tr không nắng phòng ngủ máy lạnh 18m2 15tr",  # lap 2 lan
    "ơ hay cái này là cái gì thế",             # vo nghia
    "cho tôi gặp quản lý",                     # doi gap nguoi
    "máy lạnh 15tr 18m2 😅 ko nắng, pn nhé",   # emoji + viet tat tron
    "tablet 999999999999999 đồng",             # so khong lo
    "'; DROP TABLE bookings; --",              # SQL injection thu
]


def main() -> None:
    c = TestClient(app)
    loi = []

    # cau don
    for cau in CAU_QUAI:
        try:
            r = c.post("/api/chat", json={"tin_nhan": cau})
            if r.status_code >= 500:
                loi.append((cau[:40], f"HTTP {r.status_code}"))
                continue
            d = r.json()
            if r.status_code == 200 and not (d.get("text") or "").strip():
                loi.append((cau[:40], "text RONG"))
        except Exception as e:                                     # noqa: BLE001
            loi.append((cau[:40], f"EXC {type(e).__name__}: {e}"))

    # chuoi phien ac y
    try:
        r = c.post("/api/chat", json={"tin_nhan": "hi", "phien_id": "khong-ton-tai-123"})
        assert r.status_code == 200 and r.json()["text"].strip()

        # doi nganh lien tuc roi so sanh (bang cu cua nganh TRUOC)
        pid = None
        for cau in ["tablet man 11 inch 10tr", "thế còn đồng hồ?", "so sánh máy 1 và máy 2"]:
            r = c.post("/api/chat", json={"tin_nhan": cau, "phien_id": pid}).json()
            pid = r["phien_id"]
            assert (r.get("text") or "").strip(), f"rong tai: {cau}"
        print("[chuoi doi nganh + so sanh] loai cuoi:", r["loai"])
        print("  ", r["text"][:120].replace("\n", " | "))
    except Exception as e:                                         # noqa: BLE001
        loi.append(("chuoi phien", f"{type(e).__name__}: {e}"))

    if loi:
        print(f"\nBUG: {len(loi)} ca")
        for cau, l in loi:
            print(f"  - [{cau}] {l}")
        sys.exit(1)
    print(f"\nOK het {len(CAU_QUAI)} cau quai + chuoi phien: khong 500, khong text rong.")


if __name__ == "__main__":
    main()
