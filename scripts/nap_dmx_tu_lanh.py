# -*- coding: utf-8 -*-
"""Nap sheet 'Tu Lanh' (du lieu THAT DMX) -> data/processed/tu_lanh.csv

Chay:  python scripts/nap_dmx_tu_lanh.py

Chon truc theo do phu do duoc tren 1.692 dong that (khong doan):
  So nguoi su dung  74%  -> LOC CUNG (hang tu cong bo tu cho may nguoi -
                            cung vai voi 'Pham vi su dung' ben may lanh)
  Dung tich su dung 66%  -> truc suc chua; thieu thi roi ve Dung tich tong (80%)
                            nhung DANH DAU nguon la 'tong' (TC-006: khi noi suc
                            chua thuc te phai uu tien dung tich su dung)
  Dien nang (kWh/nam) 76% -> truc tiet kiem dien (thap = tot). Ben tu lanh cot
                            nay la so that, khac hàn cot rac ben may lanh.
  Ngang/Cao/Sau     33%  -> loc hoc bep; thieu thi KHONG doan, noi ro
  Kieu dang         96%  -> loc side-by-side/mini...
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.parse_dmx import la_rong, parse_gia, parse_qua  # noqa: E402

GOC = Path("data/raw/Spec_cate_gia.xlsx")
RA = Path("data/processed/tu_lanh.csv")

COT = [
    "ma_sp", "ten", "hang", "nguoi_min", "nguoi_max", "dung_tich_lit",
    "dung_tich_la_tong", "dien_kwh_nam", "ngang_cm", "cao_cm", "sau_cm",
    "kieu_dang", "so_cua", "inverter", "gia", "gia_goc", "qua", "ngan_da_lit",
]


def parse_so_nguoi(s) -> tuple[float, float] | None:
    """'3 - 4 nguoi' -> (3,4) | 'Tren 5 nguoi' -> (5,99) | 'Duoi 2' -> (1,2)"""
    if la_rong(s):
        return None
    t = str(s).lower()
    m = re.search(r"(\d+)\s*-\s*(\d+)", t)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"trên\s*(\d+)", t)
    if m:
        return float(m.group(1)), 99.0
    m = re.search(r"dưới\s*(\d+)", t)
    if m:
        return 1.0, float(m.group(1))
    m = re.search(r"(\d+)", t)
    return (float(m.group(1)),) * 2 if m else None


def parse_lit(s) -> float | None:
    if la_rong(s):
        return None
    m = re.search(r"([\d.]+)\s*l", str(s).lower())
    return float(m.group(1)) if m else None


def parse_cm(s) -> float | None:
    """'59' hoac '59.5 cm' -> cm. Gia tri >300 chac la mm -> chia 10."""
    if la_rong(s):
        return None
    m = re.search(r"([\d.]+)", str(s))
    if not m:
        return None
    v = float(m.group(1))
    return v / 10 if v > 300 else v


def parse_kwh(s) -> float | None:
    """Dien nang tieu thu tu lanh: so thuan (kWh/nam). Loai gia tri vo ly."""
    if la_rong(s):
        return None
    m = re.search(r"([\d.]+)", str(s))
    if not m:
        return None
    v = float(m.group(1))
    return v if 50 <= v <= 2000 else None      # ngoai dai nay la don vi khac/rac


def main() -> None:
    wb = openpyxl.load_workbook(GOC, data_only=True, read_only=True)
    ws = wb["Tủ Lạnh"]
    rows = ws.iter_rows(values_only=True)
    hdr = list(next(rows))
    idx = {h: i for i, h in enumerate(hdr)}

    def g(r, ten):
        i = idx.get(ten)
        return r[i] if i is not None and i < len(r) else None

    ra, dem = [], {"tong": 0, "co_gia": 0, "co_nguoi": 0, "co_dt": 0, "co_kwh": 0, "co_kich_thuoc": 0}
    for r in rows:
        if not any(r):
            continue
        dem["tong"] += 1

        nguoi = parse_so_nguoi(g(r, "Số người sử dụng"))
        gia, gia_goc = parse_gia(g(r, "giá gốc"), g(r, "giá khuyến mãi"))
        dt_sd = parse_lit(g(r, "Dung tích sử dụng"))
        dt_tong = parse_lit(g(r, "Dung tích tổng"))
        kwh = parse_kwh(g(r, "Điện năng tiêu thụ"))
        ngang, cao, sau = (parse_cm(g(r, c)) for c in ("Ngang", "Cao", "Sâu"))

        if nguoi:
            dem["co_nguoi"] += 1
        if gia:
            dem["co_gia"] += 1
        if dt_sd or dt_tong:
            dem["co_dt"] += 1
        if kwh:
            dem["co_kwh"] += 1
        if ngang and cao and sau:
            dem["co_kich_thuoc"] += 1

        # Khong gia hoac khong biet cho may nguoi -> khong tu van duoc.
        if not gia or not nguoi:
            continue

        hang = str(g(r, "brand") or "").strip()
        ma = str(g(r, "sku") or g(r, "model_code") or "").strip()
        dung_tich = dt_sd if dt_sd is not None else dt_tong

        ra.append({
            "ma_sp": ma,
            "ten": f"{hang} {g(r, 'model_code')}".strip(),
            "hang": hang,
            "nguoi_min": nguoi[0],
            "nguoi_max": nguoi[1],
            "dung_tich_lit": "" if dung_tich is None else dung_tich,
            # TC-006: phai phan biet dung tich SU DUNG vs TONG khi noi suc chua
            "dung_tich_la_tong": int(dt_sd is None and dt_tong is not None),
            "dien_kwh_nam": "" if kwh is None else kwh,
            "ngang_cm": "" if ngang is None else ngang,
            "cao_cm": "" if cao is None else cao,
            "sau_cm": "" if sau is None else sau,
            "kieu_dang": str(g(r, "Kiểu dáng") or "").strip(),
            "so_cua": str(g(r, "Số cửa") or "").strip(),
            "inverter": int("inverter" in str(g(r, "Công nghệ tiết kiệm điện") or "").lower()),
            "gia": gia,
            "gia_goc": gia_goc or gia,
            "qua": parse_qua(g(r, "khuyến mãi quà")),
            "ngan_da_lit": ("" if (nd := parse_lit(g(r, "Dung tích ngăn đá"))) is None else nd),
        })

    RA.parent.mkdir(parents=True, exist_ok=True)
    with open(RA, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT)
        w.writeheader()
        w.writerows(ra)

    t = dem["tong"]
    print(f"Doc {t} dong tu lanh that")
    for k, nhan in [("co_nguoi", "So nguoi (-> loc cung)"), ("co_gia", "Gia"),
                    ("co_dt", "Dung tich"), ("co_kwh", "Dien kWh/nam"),
                    ("co_kich_thuoc", "Du 3 kich thuoc")]:
        print(f"  {nhan:26s} {dem[k]:5d}/{t} ({100*dem[k]/t:3.0f}%)")
    print(f"\n=> Catalog tu lanh ban duoc: {len(ra)} tu -> {RA}")


if __name__ == "__main__":
    main()
