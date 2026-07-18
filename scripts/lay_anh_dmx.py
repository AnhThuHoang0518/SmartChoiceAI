# -*- coding: utf-8 -*-
"""Lay URL anh CHINH CHU dienmayxanh.com cho tung SKU theo productidweb.

Chay TREN MAY WAN (can mang):  python scripts/lay_anh_dmx.py

Can cu (kiem chung thuc nghiem 19/07, khong doan):
  - Cot 'productidweb' trong Spec_cate_gia.xlsx = product id tren web DMX
    (doi chieu: Casper QC-09IU36A productidweb=334018 khop id trong URL anh
    cua chinh trang san pham do).
  - og:image cua trang san pham co dang cdn.tgdd.vn/<yyyy>/<mm>/timerseo/<id>.jpg
  - CDN tra 200 ca voi id khong ton tai -> phai kiem content-type la anh VA
    kich thuoc >= NGUONG (anh that vai chuc KB, placeholder thi nho).

Ket qua: data/processed/anh_sp.json  {ma_sp: url}  - nam trong .gitignore
(data/processed/*), scp len VPS nhu cac CSV. Anh chi de HIEN THI kem nguon
"dienmayxanh.com"; khong anh -> UI giu icon nganh, khong do anh bua.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import openpyxl
import requests

GOC = Path("data/raw/Spec_cate_gia.xlsx")
RA = Path("data/processed/anh_sp.json")

# thu lan luot cac prefix nam/thang (timerseo gen theo dot; 2026/05 dang trung
# nhieu nhat theo tham do). Trung o prefix nao thi dung o do.
PREFIX = ["2026/05", "2026/06", "2026/07", "2026/04", "2026/03",
          "2026/02", "2026/01", "2025/12", "2025/11", "2025/10",
          "2025/09", "2025/08", "2025/07", "2025/06", "2025/05"]
NGUONG_BYTE = 3000                       # anh that >= 3KB; be hon coi nhu khong co


UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Referer": "https://www.dienmayxanh.com/"}
_DEBUG_CON = 3                             # in chan doan 3 ca dau de biet CDN tra gi


def anh_hop_le(url: str) -> bool:
    """GET kem User-Agent (CDN chan HEAD/request tran - lan chay dau trung 0/100).
    Anh hop le = 200 + content-type image + kich thuoc >= NGUONG (doc chunk dau
    neu server khong bao content-length)."""
    global _DEBUG_CON
    try:
        r = requests.get(url, timeout=8, headers=UA, stream=True, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        cl = r.headers.get("content-length")
        if _DEBUG_CON > 0:
            _DEBUG_CON -= 1
            print(f"    [chan doan] {r.status_code} | {ct} | len={cl} | {url[-34:]}")
        if r.status_code != 200 or not ct.startswith("image/"):
            return False
        if cl is not None:
            return int(cl) >= NGUONG_BYTE
        n = 0
        for chunk in r.iter_content(4096):
            n += len(chunk)
            if n >= NGUONG_BYTE:
                return True
        return n >= NGUONG_BYTE
    except Exception:
        return False


def main() -> None:
    wb = openpyxl.load_workbook(GOC, data_only=True, read_only=True)
    ra: dict[str, str] = {}
    if RA.exists():                       # chay lai thi tiep tuc, khong lam lai tu dau
        ra = json.loads(RA.read_text(encoding="utf-8"))

    tong = trung = 0
    for ws in wb:
        rows = ws.iter_rows(values_only=True)
        try:
            hdr = list(next(rows))
            i_sku = hdr.index("sku") if "sku" in hdr else hdr.index("model_code")
            i_id = hdr.index("productidweb")
            i_gia = hdr.index("giá gốc")
            i_km = hdr.index("giá khuyến mãi")
        except (StopIteration, ValueError):
            continue
        for r in rows:
            if not any(r) or not (r[i_gia] or r[i_km]):
                continue                  # chi lay SKU dang ban duoc (co gia) - khop catalog
            ma = str(r[i_sku] or "").strip()
            pid = str(r[i_id] or "").strip()
            if not ma or not pid or ma in ra:
                continue
            tong += 1
            for px in PREFIX:
                url = f"https://cdn.tgdd.vn/{px}/timerseo/{pid}.jpg"
                if anh_hop_le(url):
                    ra[ma] = url
                    trung += 1
                    break
            time.sleep(0.12)              # lich su voi CDN nguoi ta
            if tong % 100 == 0:
                print(f"  ... {tong} SKU, trung {trung}")
                RA.parent.mkdir(parents=True, exist_ok=True)
                RA.write_text(json.dumps(ra, ensure_ascii=False, indent=0), encoding="utf-8")

    RA.parent.mkdir(parents=True, exist_ok=True)
    RA.write_text(json.dumps(ra, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"\nXong: {trung}/{tong} SKU co anh chinh chu -> {RA}")
    print("Buoc sau: scp file nay len VPS cung cho voi cac CSV:")
    print("  scp data\\processed\\anh_sp.json root@45.117.170.223:/opt/smartchoice/data/processed/")


if __name__ == "__main__":
    main()
