# -*- coding: utf-8 -*-
"""Parser cho du lieu THAT cua Dien May Xanh (Spec_cate_gia.xlsx).

Vi sao can file rieng: du lieu that khong giong bat cu gia dinh nao. Do do
tach parser ra day de test duoc tung ham, va de khi doi tac cap API that thi
chi thay tang nap chu khong dung vao logic tu van.

Ty le doc duoc do tren 1039 dong may lanh that:
  Pham vi su dung : 91%  -> loc cung dua vao day
  Nhan nang luong : 100% doc ra CSPF
  Do on           : 98%  (685/696 dong co du lieu)
  Cong suat dau ra: 1%   -> VUT BO, khong dung duoc
  Dien nang tt    : rac ('0','1','2') -> VUT BO
"""
from __future__ import annotations

import re

# Cac chuoi dong nghia voi "khong co du lieu" trong file that.
RONG = {"", "không", "không có", "đang cập nhật", "hãng không công bố", "none"}


def la_rong(x) -> bool:
    return x is None or str(x).strip().lower() in RONG


def parse_pham_vi(s) -> tuple[float, float] | None:
    """'Tu 15 - 20m2 (tu 40 den 60m3)' -> (15.0, 20.0)

    Day la thu thay the ca bang tra m2->HP: chinh hang da cong bo may nay
    danh cho phong bao nhieu m2. Chinh xac hon suy dien tu cong suat.

    Bat buoc cat phan trong ngoac TRUOC khi bat so: '(tu 120 - 180m3)' cung co
    dang 'a - b', bat nham la ra pham vi 120-180m2.
    """
    if la_rong(s):
        return None
    t = str(s).split("(")[0].strip()
    m = re.search(r"dưới\s*([\d.]+)\s*m²", t, re.I)
    if m:
        return 0.0, float(m.group(1))
    m = re.search(r"([\d.]+)\s*-\s*([\d.]+)\s*m²", t, re.I)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"trên\s*([\d.]+)\s*m²", t, re.I)
    if m:
        return float(m.group(1)), 999.0
    return None


def parse_do_on(s) -> float | None:
    """'Dan lanh: 45/34/29 dB - Dan nong: 51 dB' -> 29.0

    Lay MIN cua dan lanh, vi:
      - dan nong dat ngoai troi, khach khong nghe -> bo qua.
      - '45/34/29' la 3 muc quat cao/vua/thap. Min = che do em, la so cac hang
        deu cong bo nen so sanh duoc, va la cai khach nghe luc ngu.
    """
    if la_rong(s):
        return None
    t = str(s)
    m = re.search(r"dàn lạnh[:\s]*([\d./\s-]+?)\s*dB", t, re.I)
    if m:
        so = re.findall(r"[\d.]+", m.group(1))
        return min(float(x) for x in so) if so else None
    # Khong ghi ro dan nao: '33/50 dB' -> thuong la lanh/nong -> lay min
    m = re.search(r"([\d.]+)\s*/\s*([\d.]+)\s*dB", t)
    if m:
        return min(float(m.group(1)), float(m.group(2)))
    m = re.search(r"([\d.]+)\s*dB", t)
    return float(m.group(1)) if m else None


def parse_nhan_nang_luong(s) -> tuple[float | None, float | None]:
    """'5 sao (Hieu suat nang luong 6.23)' -> (5.0, 6.23)

    CSPF (so trong ngoac) moi la hieu suat THAT - cao hon = tot dien hon.
    Cot 'Dien nang tieu thu' cua file that chi co '0','1','2' -> vo nghia,
    nen CSPF la truc tiet kiem dien duy nhat dung duoc.
    """
    if la_rong(s):
        return None, None
    t = str(s)
    sao = re.search(r"([\d.]+)\s*sao", t, re.I)
    cspf = re.search(r"năng lượng\s*([\d.]+)", t, re.I)
    return (
        float(sao.group(1)) if sao else None,
        float(cspf.group(1)) if cspf else None,
    )


def parse_gia(goc, km) -> tuple[int | None, int | None]:
    """Tra (gia_ban, gia_goc). Uu tien gia khuyen mai - do la gia khach tra that."""

    def _so(x):
        if la_rong(x):
            return None
        try:
            return int(float(str(x).replace(",", "").replace(".", "")))
        except ValueError:
            return None

    g, k = _so(goc), _so(km)
    if k and g and k < g:
        return k, g          # co khuyen mai that
    return (k or g), (g or k)


def parse_inverter(s) -> bool:
    return "không" not in str(s or "").lower() and "inverter" in str(s or "").lower()


def parse_qua(v) -> str:
    """Cot 'khuyen mai qua' -> chuoi gon cho UI/tu van.

    Nhieu dong 1 o (moi dong 1 mon) -> lay 2 mon dau, cat 180 ky tu. Van la
    NGUYEN VAN tu du lieu, khong sinh chu moi - chi cat gon.
    """
    if la_rong(v):
        return ""
    phan = [re.sub(r"\s*\(click xem chi tiết\)", "", x.strip(), flags=re.I)
            for x in re.split(r"[\n|]", str(v)) if x.strip()]
    return " · ".join(phan[:2])[:180]
