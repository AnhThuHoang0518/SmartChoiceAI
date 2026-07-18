# -*- coding: utf-8 -*-
"""HIEU Y MO bang embedding - khach noi MUC DICH ma khong goi ten san pham.

Vd: "cho con hoc online" -> may tinh bang / may tinh de ban; "giu do dong
lanh ban hang" -> tu dong; "hat karaoke tai nha" -> micro.

AN TOAN TUYET DOI: embedding CHI de GOI Y nganh (chip bam duoc), khach van
phai chon - KHONG tu chot nganh, KHONG tu dat nguong, KHONG bia san pham.
Regex/keyword chay TRUOC (nhanh, chac); embedding chi vot khi keyword tit.
Khong co khoa FPT -> tra rong -> hanh vi cu giu nguyen (test luat van xanh).

Dung Vietnamese_Embedding cua FPT (docs chinh thuc: POST /embeddings, OpenAI
compat). Nhung con so trong tu van van do CODE tinh - embedding khong dung o
buoc loc/cham diem.
"""
from __future__ import annotations

import math
import os

# nganh -> vai cau MUC DICH tieu bieu (khach hay noi kieu nay). Nhan hien thi
# de dua vao chip goi y. 2 vertical + 11 nganh khung.
_MUC_DICH = {
    "máy lạnh": ["làm mát phòng cho đỡ nóng", "điều hòa không khí trong nhà"],
    "tủ lạnh": ["bảo quản thức ăn rau củ hằng ngày", "giữ đồ mát trong bếp"],
    "máy giặt": ["giặt quần áo cho gia đình", "giặt đồ đỡ tốn công"],
    "máy sấy": ["sấy khô quần áo mùa mưa nồm ẩm", "hong đồ nhanh khô"],
    "máy rửa chén": ["rửa bát đĩa dọn bếp sau khi ăn", "đỡ phải rửa chén tay"],
    "tủ đông": ["trữ đông thực phẩm số lượng nhiều", "quán bán hàng đông lạnh kem cá thịt"],
    "máy nước nóng": ["tắm nước ấm mùa lạnh", "có nước nóng dùng trong nhà tắm"],
    "máy tính bảng": ["cho con học online xem bài giảng", "xem phim đọc sách giải trí cầm tay"],
    "đồng hồ thông minh": ["theo dõi sức khỏe đếm bước", "chạy bộ tập thể thao đo nhịp tim"],
    "màn hình": ["làm việc văn phòng màn hình lớn", "chơi game hoặc làm đồ họa"],
    "máy tính để bàn": ["làm việc văn phòng ở nhà", "chơi game cấu hình mạnh"],
    "máy in": ["in tài liệu giấy tờ tại nhà", "in ảnh in văn bản văn phòng"],
    "micro": ["hát karaoke tại nhà", "thu âm livestream nói chuyện"],
}

_NGUONG = 0.62                             # duoi nguong nay coi nhu khong ro -> khong goi y bua
_BANK: dict[str, list[float]] | None = None
_KHONG_CO_FPT = False


def _khoa() -> str | None:
    if (os.getenv("LLM_NHA_CUNG_CAP") or "").strip().lower() != "fpt":
        return None
    return (os.getenv("LLM_API_KEY") or "").strip() or None


def _embed(texts: list[str]) -> list[list[float]] | None:
    import requests

    khoa = _khoa()
    if not khoa:
        return None
    try:
        r = requests.post(
            "https://mkp-api.fptcloud.com/embeddings",
            headers={"Authorization": f"Bearer {khoa}"},
            json={"input": texts, "model": os.getenv("EMBED_MODEL", "Vietnamese_Embedding")},
            timeout=15,
        )
        r.raise_for_status()
        return [d["embedding"] for d in r.json()["data"]]
    except Exception:
        return None


def _cosine(a: list[float], b: list[float]) -> float:
    t = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return t / (na * nb)


def _nap_bank() -> dict[str, list[float]] | None:
    """Embed cac cau muc dich 1 lan, giu trong RAM. Loi/khong co FPT -> None."""
    global _BANK, _KHONG_CO_FPT
    if _BANK is not None or _KHONG_CO_FPT:
        return _BANK
    cau, nganh = [], []
    for ng, ds in _MUC_DICH.items():
        for c in ds:
            cau.append(c)
            nganh.append(ng)
    vec = _embed(cau)
    if not vec:
        _KHONG_CO_FPT = True
        return None
    # gom trung binh vector cua moi nganh (cac cau muc dich cua no)
    tong: dict[str, list[float]] = {}
    dem: dict[str, int] = {}
    for ng, v in zip(nganh, vec):
        if ng not in tong:
            tong[ng] = [0.0] * len(v)
            dem[ng] = 0
        tong[ng] = [s + x for s, x in zip(tong[ng], v)]
        dem[ng] += 1
    _BANK = {ng: [s / dem[ng] for s in tong[ng]] for ng in tong}
    return _BANK


def goi_y_nganh(text: str, toi_da: int = 3) -> list[str]:
    """Tra danh sach ten nganh GAN nghia nhat voi muc dich khach - de lam chip.
    Rong = khong ro / khong co FPT -> caller giu hanh vi cu (liet ke chung)."""
    bank = _nap_bank()
    if not bank:
        return []
    v = _embed([text])
    if not v:
        return []
    v = v[0]
    xep = sorted(((ng, _cosine(v, vec)) for ng, vec in bank.items()),
                 key=lambda x: -x[1])
    return [ng for ng, d in xep[:toi_da] if d >= _NGUONG]
