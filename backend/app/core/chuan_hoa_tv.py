# -*- coding: utf-8 -*-
"""Chuan hoa tieng Viet mua sam THAT truoc khi dua cho LLM trich o nhu cau.

De bai ghi ro phai hieu: "tieng Viet tu nhien, co dau/khong dau, van noi, viet
tat va ngon ngu mua sam pho thong", "co the co loi chinh ta, viet tat, tu dia
phuong, don vi do nhu m2, HP, BTU, GB, lit, inch".

Tang nay la CODE, khong phai LLM. Ly do: viet tat mua sam la tap dong, huu han
va biet truoc -> tra bang vua nhanh (0ms) vua chac. De LLM tu doan '20tr' thi
thinh thoang no ra 20 nghin.

KHONG lam khoi phuc dau tieng Viet day du (can model rieng). Thay vao do:
so khop KHONG DAU - nguoi dung go 'may lanh' hay 'máy lạnh' deu ra cung ket qua.
"""
from __future__ import annotations

import re
import unicodedata

# Viet tat -> day du. Khop tren ban KHONG DAU nen chi can viet khong dau.
VIET_TAT = {
    r"\btk dien\b": "tiết kiệm điện",
    r"\btkd\b": "tiết kiệm điện",
    r"\bdt\b": "diện tích",
    r"\bml\b": "máy lạnh",
    r"\bdhkk\b": "máy lạnh",
    r"\bdieu hoa\b": "máy lạnh",
    r"\bmay lanh\b": "máy lạnh",
    r"\bp ngu\b": "phòng ngủ",
    r"\bpn\b": "phòng ngủ",
    r"\bpk\b": "phòng khách",
    r"\bp khach\b": "phòng khách",
    r"\bit on\b": "ít ồn",
    r"\bem\b(?=\s*(?:hon|nhat))": "êm",
    r"\btra gop\b": "trả góp",
    r"\bkm\b": "khuyến mãi",
    r"\bbh\b": "bảo hành",
}


def bo_dau(s: str) -> str:
    """'máy lạnh' -> 'may lanh'. Dung de SO KHOP, khong dung de hien thi."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", s).replace("đ", "d").replace("Đ", "D")


def chuan_hoa_tien(s: str) -> str:
    """'20tr' -> '20000000'. '500k' -> '500000'.

    Lam o day chu khong de LLM doan: '20tr' ra '20 nghin' la sai gia 1000 lan,
    ma sai gia la thu de bai cham nang nhat.
    """
    def _tr(m):
        v = float(m.group(1).replace(",", "."))
        return str(int(v * 1_000_000))

    def _k(m):
        v = float(m.group(1).replace(",", "."))
        return str(int(v * 1_000))

    s = re.sub(r"\b([\d.,]+)\s*(?:tr|trieu|triệu)\b", _tr, s, flags=re.I)
    s = re.sub(r"\b([\d.,]+)\s*(?:k|nghin|nghìn)\b", _k, s, flags=re.I)
    return s


def chuan_hoa_don_vi(s: str) -> str:
    """'18m2', '18 met vuong', '18m^2' -> '18m²'."""
    return re.sub(r"\b(\d+(?:[.,]\d+)?)\s*(?:m2|m\^2|m²|met vuong|mét vuông)\b",
                  r"\1m²", s, flags=re.I)


def chuan_hoa(s: str) -> str:
    """Ham chinh: van ban tho -> van ban da chuan hoa cho LLM trich o nhu cau."""
    goc = (s or "").strip()
    if not goc:
        return ""

    # Mo viet tat: khop tren ban khong dau, thay tren ban goc theo vi tri.
    khong_dau = bo_dau(goc).lower()
    thay: list[tuple[int, int, str]] = []
    for mau, day_du in VIET_TAT.items():
        for m in re.finditer(mau, khong_dau):
            thay.append((m.start(), m.end(), day_du))
    thay.sort(key=lambda x: -x[0])          # thay tu cuoi len de khong lech vi tri
    ra = goc
    for i, j, day_du in thay:
        ra = ra[:i] + day_du + ra[j:]

    return chuan_hoa_don_vi(chuan_hoa_tien(ra))
