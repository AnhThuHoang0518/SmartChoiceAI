# -*- coding: utf-8 -*-
"""LLM DE XUAT UNG VIEN nganh tu cau mo ho - lop vot CUOI khi luat (regex tinh
huong) va embedding deu tit.

AN TOAN TUYET DOI (nguyen tac 'thong minh nhung khong co quyen'):
- LLM CHI duoc chon 1 ten trong DANH SACH DONG cac nganh CO du lieu, hoac
  'khong_ro'. Dau ra ngoai danh sach -> loai bo -> None (khong bia nganh moi).
- KHONG tu chot nganh: ung vien van phai qua buoc khach xac nhan o router.
- KHONG sinh so: gia/ton kho/xep hang van do CODE tinh tu DB.
- LuatLLM / khong co khoa -> sinh() tra '' -> None -> hanh vi cu giu nguyen,
  test luat van xanh, khong phu thuoc mang.
"""
from __future__ import annotations

import json
import re

from backend.app.core.chuan_hoa_tv import bo_dau


def _danh_sach_nganh() -> list[str]:
    """13 nganh CO du lieu (2 vertical + 11 khung) - ten hien thi."""
    from backend.app.nganh.khung import cac_nganh
    return ["máy lạnh", "tủ lạnh"] + [ng.ten_hien_thi for ng in cac_nganh()]


_HE_THONG = (
    "Bạn là bộ định tuyến nhu cầu điện máy. Khách mô tả TÌNH HUỐNG hoặc VẤN ĐỀ "
    "trong đời sống (không gọi tên sản phẩm). Nhiệm vụ duy nhất: chọn ĐÚNG MỘT "
    "ngành hàng phù hợp nhất trong DANH SÁCH cho sẵn, hoặc 'khong_ro' nếu không "
    "đủ căn cứ.\n"
    "QUY TẮC: chỉ được chọn tên y hệt một mục trong danh sách; KHÔNG bịa ngành "
    "ngoài danh sách; KHÔNG giải thích; KHÔNG nêu giá, thương hiệu hay model.\n"
    'Chỉ trả JSON: {"nganh": "<tên trong danh sách hoặc khong_ro>"}'
)


def de_xuat_nganh_llm(text: str, llm) -> str | None:
    """Tra TEN HIEN THI nganh (khop chinh xac danh sach dong) hoac None.

    None khi: LLM tra rong / sai khuon / chon ten ngoai danh sach / 'khong_ro'.
    """
    if not (text or "").strip():
        return None
    ds = _danh_sach_nganh()
    nguoi_dung = (
        f"DANH SÁCH NGÀNH: {', '.join(ds)}\n"
        f"CÂU KHÁCH: {text}\n"
        'Trả JSON {"nganh": "..."}'
    )
    try:
        raw = llm.sinh(_HE_THONG, nguoi_dung, json_mode=True) or ""
    except Exception:
        return None
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        nganh = (json.loads(m.group(0)).get("nganh") or "").strip()
    except Exception:
        return None
    kd = bo_dau(nganh).lower()
    if not kd or kd in ("khong ro", "khong_ro"):
        return None
    # Chi chap nhan khi KHOP CHINH XAC ten trong danh sach dong -> chong bia.
    for ten in ds:
        if bo_dau(ten).lower() == kd:
            return ten
    return None
