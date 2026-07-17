# -*- coding: utf-8 -*-
"""Nap Spec_cate_gia.xlsx (du lieu THAT cua DMX) -> data/processed/may_lanh.csv

Chay:  python scripts/nap_dmx.py

Tach lam 2 tang co chu y:
  - Tang nay doc file goc NDA (data/raw/, da gitignore) va chuan hoa.
  - Tang chay that (backend) chi doc data/processed/ da sach.
Khi doi tac cap API that thi chi thay file nay, logic tu van khong dung toi.

In ra ty le doc duoc tung cot - day la SO LIEU dua thang len slide de chung
minh he thong chay tren du lieu that chu khong phai du lieu tu bia cho dep.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.parse_dmx import (  # noqa: E402
    la_rong,
    parse_do_on,
    parse_gia,
    parse_inverter,
    parse_nhan_nang_luong,
    parse_pham_vi,
)

GOC = Path("data/raw/Spec_cate_gia.xlsx")
RA = Path("data/processed/may_lanh.csv")

COT = [
    "ma_sp", "ten", "hang", "pham_vi_min", "pham_vi_max", "gia", "gia_goc",
    "do_on_db", "cspf", "sao", "inverter", "lam_lanh_nhanh", "loai_may",
]

# Cong nghe lam lanh nhanh - cot 'Cong nghe lam lanh' phu 93%.
TU_KHOA_TURBO = ("turbo", "powerful", "jet cool", "fast", "nhanh", "h-pcm")


def nap(sheet: str = "Máy lạnh") -> list[dict]:
    wb = openpyxl.load_workbook(GOC, data_only=True, read_only=True)
    ws = wb[sheet]
    rows = ws.iter_rows(values_only=True)
    hdr = list(next(rows))
    idx = {h: i for i, h in enumerate(hdr)}

    def g(r, ten):
        i = idx.get(ten)
        return r[i] if i is not None and i < len(r) else None

    ra, dem = [], {"tong": 0, "co_pham_vi": 0, "co_gia": 0, "co_do_on": 0, "co_cspf": 0}
    for r in rows:
        if not any(r):
            continue
        dem["tong"] += 1

        pv = parse_pham_vi(g(r, "Phạm vi sử dụng"))
        gia, gia_goc = parse_gia(g(r, "giá gốc"), g(r, "giá khuyến mãi"))
        do_on = parse_do_on(g(r, "Độ ồn"))
        sao, cspf = parse_nhan_nang_luong(g(r, "Nhãn năng lượng"))

        if pv:
            dem["co_pham_vi"] += 1
        if gia:
            dem["co_gia"] += 1
        if do_on is not None:
            dem["co_do_on"] += 1
        if cspf is not None:
            dem["co_cspf"] += 1

        # Thieu pham vi hoac gia -> khong tu van duoc. Thieu gia thi khong biet
        # co vua tui khach khong; thieu pham vi thi khong biet co du tai khong.
        # Doan bua ca hai deu la tu van sai.
        if not pv or not gia:
            continue

        hang = str(g(r, "brand") or "").strip()
        ma = str(g(r, "sku") or g(r, "model_code") or "").strip()
        clm = str(g(r, "Công nghệ làm lạnh") or "").lower()

        ra.append(
            {
                "ma_sp": ma,
                # File that KHONG co cot ten san pham - chi model_code dang so.
                # Ghep hang + ma de con goi ten duoc. API that cua doi tac se co ten.
                "ten": f"{hang} {g(r, 'model_code')}".strip(),
                "hang": hang,
                "pham_vi_min": pv[0],
                "pham_vi_max": pv[1],
                "gia": gia,
                "gia_goc": gia_goc or gia,
                "do_on_db": "" if do_on is None else do_on,
                "cspf": "" if cspf is None else cspf,
                "sao": "" if sao is None else sao,
                "inverter": int(parse_inverter(g(r, "Loại Inverter"))),
                "lam_lanh_nhanh": int(any(k in clm for k in TU_KHOA_TURBO)),
                "loai_may": str(g(r, "Loại máy") or "").strip(),
            }
        )
    return ra, dem


def main() -> None:
    ra, dem = nap()
    RA.parent.mkdir(parents=True, exist_ok=True)
    with open(RA, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT)
        w.writeheader()
        w.writerows(ra)

    t = dem["tong"]
    print(f"Doc {t} dong may lanh that tu {GOC}")
    print("Ty le doc duoc tung cot:")
    for k, nhan in [
        ("co_pham_vi", "Pham vi su dung (-> loc cung)"),
        ("co_gia", "Gia (goc hoac KM)"),
        ("co_do_on", "Do on (-> truc do on)"),
        ("co_cspf", "CSPF (-> truc tiet kiem dien)"),
    ]:
        print(f"  {nhan:34s} {dem[k]:4d}/{t}  ({100*dem[k]/t:3.0f}%)")
    print(f"\n=> Catalog ban duoc: {len(ra)} may (co ca pham vi VA gia) -> {RA}")


if __name__ == "__main__":
    main()
