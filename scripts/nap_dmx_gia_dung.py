# -*- coding: utf-8 -*-
"""Nap cac sheet GIA DUNG (may giat, may say...) -> data/processed/*.csv

Chay:  python scripts/nap_dmx_gia_dung.py

Moi nganh la 1 muc trong SPEC: sheet nao, cot nao parse kieu gi. Them nganh
gia dung moi = them 1 muc SPEC + 1 file configs/nganh/*.json. Khong sua code.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.services.parse_dmx import la_rong, parse_gia  # noqa: E402

GOC = Path("data/raw/Spec_cate_gia.xlsx")


def p_khoang_nguoi(s):
    """'Tu 3 - 5 nguoi (8 - 9 kg)' -> (3,5). Phai cat phan ngoac truoc -
    khong thi '(8 - 9 kg)' bi bat nham thanh khoang nguoi (bay giong m3 ben
    may lanh)."""
    if la_rong(s):
        return None
    t = str(s).split("(")[0].lower()
    m = re.search(r"(\d+)\s*-\s*(\d+)", t)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"trên\s*(\d+)", t)
    if m:
        return float(m.group(1)), 99.0
    m = re.search(r"dưới\s*(\d+)", t)
    if m:
        return 1.0, float(m.group(1))
    return None


def p_so(s, don_vi=""):
    """'9 Kg' -> 9 | '750 vong/phut' -> 750 | '60°C' -> 60 | '34.7 Wh/kg' -> 34.7"""
    if la_rong(s):
        return None
    m = re.search(r"([\d.]+)", str(s))
    return float(m.group(1)) if m else None


def p_cm(s):
    if la_rong(s):
        return None
    m = re.search(r"([\d.]+)", str(s))
    if not m:
        return None
    v = float(m.group(1))
    return v / 10 if v > 300 else v


def p_nam(s):
    """'5 nam' -> 5 (TC-023: bao hanh dong co)."""
    if la_rong(s):
        return None
    m = re.search(r"(\d+)\s*năm", str(s).lower())
    return float(m.group(1)) if m else None


SPEC = {
    "may_giat": {
        "sheet": "Máy giặt",
        "cot": {
            "nguoi_min": ("Số người sử dụng", lambda s: (p_khoang_nguoi(s) or (None,))[0]),
            "nguoi_max": ("Số người sử dụng", lambda s: (p_khoang_nguoi(s) or (None, None))[1]),
            "tai_kg": ("Khối lượng tải chính", p_so),
            "dien_wh_kg": ("Điện năng tiêu thụ", p_so),
            "vat_vong": ("Tốc độ quay vắt tối đa", p_so),
            "bao_hanh_dc_nam": ("Bảo hành động cơ", p_nam),
            "ngang_cm": ("Ngang", p_cm),
            "sau_cm": ("Sâu", p_cm),
        },
        "chu": {"loai": "Loại sản phẩm"},
        # khong tu van duoc neu thieu:
        "bat_buoc": ["nguoi_min", "nguoi_max"],
    },
    "may_say": {
        "sheet": "Máy sấy quần áo",
        "cot": {
            "nguoi_min": ("Số người sử dụng", lambda s: (p_khoang_nguoi(s) or (None,))[0]),
            "nguoi_max": ("Số người sử dụng", lambda s: (p_khoang_nguoi(s) or (None, None))[1]),
            "tai_kg": ("Khối lượng tải chính", p_so),
            "dien_w": ("Điện năng tiêu thụ", p_so),
            "nhiet_toi_da_c": ("Nhiệt độ tối đa", p_so),
            "ngang_cm": ("Ngang", p_cm),
            "cao_cm": ("Cao", p_cm),
            "sau_cm": ("Sâu", p_cm),
        },
        "chu": {"loai": "Loại sản phẩm"},
        # may say: 'So nguoi' chi 86% nhung 'tai_kg' 100% -> tai la truc chinh,
        # khoang nguoi chi de loc khi CO. Bat buoc: tai hoac nguoi deu chap nhan
        # -> de trong, loc mem trong config.
        "bat_buoc": ["tai_kg"],
    },
}


def nap_mot_nganh(wb, ten: str, spec: dict) -> None:
    ws = wb[spec["sheet"]]
    rows = ws.iter_rows(values_only=True)
    hdr = list(next(rows))
    idx = {h: i for i, h in enumerate(hdr)}

    def g(r, cot):
        i = idx.get(cot)
        return r[i] if i is not None and i < len(r) else None

    ra, tong = [], 0
    for r in rows:
        if not any(r):
            continue
        tong += 1
        gia, gia_goc = parse_gia(g(r, "giá gốc"), g(r, "giá khuyến mãi"))
        if not gia:
            continue
        dong = {
            "ma_sp": str(g(r, "sku") or g(r, "model_code") or "").strip(),
            "ten": f"{str(g(r, 'brand') or '').strip()} {g(r, 'model_code')}".strip(),
            "hang": str(g(r, "brand") or "").strip(),
            "gia": gia, "gia_goc": gia_goc or gia,
        }
        for c, (cot_goc, ham) in spec["cot"].items():
            v = ham(g(r, cot_goc))
            dong[c] = "" if v is None else v
        for c, cot_goc in spec["chu"].items():
            dong[c] = str(g(r, cot_goc) or "").strip()
        # thieu truong bat buoc -> khong tu van duoc, bo
        if any(dong[c] == "" for c in spec["bat_buoc"]):
            continue
        ra.append(dong)

    out = Path(f"data/processed/{ten}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ra[0].keys()))
        w.writeheader()
        w.writerows(ra)
    print(f"{ten:10s} {spec['sheet']:20s} {tong:5d} dong -> ban duoc {len(ra):4d} -> {out}")


def main() -> None:
    wb = openpyxl.load_workbook(GOC, data_only=True, read_only=True)
    for ten, spec in SPEC.items():
        nap_mot_nganh(wb, ten, spec)


if __name__ == "__main__":
    main()
