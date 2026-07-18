# -*- coding: utf-8 -*-
"""Do 6 cau tieu bieu voi LLM THAT (FPT) - chay truoc gio quay video.

Chay:  python scripts/do_llm_that.py          (can .env co khoa FPT)

Do 3 thu: giay THAT tung luot, so lan hau kiem chan, van co tu nhien khong
(in ra doc bang mat). Ton vai xu credit - dang gia.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402

CAU = [
    ("e muon mua may lanh duoi 20tr cho phong 18m2, tk dien, it on", None),
    ("co, chieu nang lam", 0),                     # noi tiep cau tren
    ("tủ lạnh cho 2 vợ chồng 2 đứa con hay trữ đông, tầm 15tr", None),
    ("tablet xiaomi màn 11 inch pin trâu tầm 10tr", None),
    ("máy nước nóng chống giật bình 20 lít tầm 4tr", None),
    ("so sánh máy 1 và máy 2", 4),                 # noi tiep cau tren
]


def main() -> None:
    c = TestClient(app)
    phien: dict[int, str] = {}
    for i, (cau, noi_tiep) in enumerate(CAU):
        pid = phien.get(noi_tiep) if noi_tiep is not None else None
        t0 = time.perf_counter()
        r = c.post("/api/chat", json={"tin_nhan": cau, "phien_id": pid}).json()
        giay = time.perf_counter() - t0
        phien[i] = r["phien_id"]
        tk = r.get("thong_ke", {})
        print(f"\n[{i + 1}] {cau[:60]}")
        print(f"    {giay:.1f}s | loai={r['loai']} | LLM={tk.get('nguon_llm', '-')} "
              f"| chan bia={tk.get('so_lan_chan_bia', 0)}")
        if tk.get("loi_da_chan"):
            print(f"    da chan: {tk['loi_da_chan']}")
        print("    " + (r["text"] or "")[:220].replace("\n", "\n    "))
        if giay > 5:
            print("    ⚠ VUOT MOC 5s")


if __name__ == "__main__":
    main()
