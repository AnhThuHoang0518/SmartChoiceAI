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

    def _ty(m):
        v = float(m.group(1).replace(",", "."))
        return str(int(v * 1_000_000_000))

    # 'ty/ti' khong dau chi khop khi co SO dung truoc -> khong dinh 'ti vi'.
    # Bai hoc tu demo that: khach go '20 tỷ' ma khong hieu -> hoi ngan sach lap
    # vo tan. Tien VN co 4 don vi noi mieng: nghin/k, trieu/tr, ty - thieu 1 la thua.
    s = re.sub(r"\b([\d.,]+)\s*(?:tỷ|tỉ|ty|ti)\b", _ty, s, flags=re.I)
    s = re.sub(r"\b([\d.,]+)\s*(?:tr|trieu|triệu)\b", _tr, s, flags=re.I)
    s = re.sub(r"\b([\d.,]+)\s*(?:k|nghin|nghìn)\b", _k, s, flags=re.I)
    return s


# ── Nganh hang ngoai pham vi demo ───────────────────────────────────────────
# File du lieu that co 14 nganh, demo moi bat may lanh. Khach hoi nganh khac
# thi phai NOI THANG, khong duoc lai cau hoi ngan sach nhu robot hong.

NGANH_KHAC = [
    (r"\btu lanh\b", "tủ lạnh"),
    (r"\bmay giat\b", "máy giặt"),
    (r"\bmay say\b", "máy sấy"),
    (r"\bmay rua (?:chen|bat)\b", "máy rửa chén"),
    (r"\btu (?:dong|mat)\b", "tủ mát/tủ đông"),
    (r"\bmay nuoc nong\b", "máy nước nóng"),
    (r"\b(?:tivi|ti vi)\b", "tivi"),
    (r"\b(?:laptop|may tinh)\b", "laptop/máy tính"),
    (r"\bdien thoai\b", "điện thoại"),
    (r"\bdong ho\b", "đồng hồ thông minh"),
    (r"\bman hinh\b", "màn hình"),
    (r"\bmay in\b", "máy in"),
]


def co_nganh_may_lanh(text: str) -> bool:
    """Khach co nhac toi may lanh (nganh dang bat trong demo) khong."""
    return bool(re.search(r"\b(may lanh|dieu hoa|dhkk|ml)\b", bo_dau(text or "").lower()))


# ── Nhan biet khach ranh ky thuat ───────────────────────────────────────────
# Sale that doi giong theo khach: khach binh dan thi noi loi ich, khach ranh
# ky thuat thi noi thang so. Nhan biet qua CHINH ngon ngu khach go - dung
# regex chu khong dung LLM: chac chan, giai trinh duoc, 0ms.

TU_KY_THUAT = (
    "cspf", "btu", "hp", "db", "decibel", "gas r32", "r32", "r410",
    "dan nong", "dan lanh", "2 chieu", "hai chieu", "cong suat lanh",
    "nhan nang luong", "eer", "seer",
)


def tu_ky_thuat_trong(text: str) -> set[str]:
    """Tap thuat ngu ky thuat xuat hien trong cau. Cong don qua ca phien:
    >=2 thuat ngu khac nhau -> khach ranh ky thuat."""
    kd = bo_dau(text or "").lower()
    return {t for t in TU_KY_THUAT if re.search(rf"\b{re.escape(t)}\b", kd)}


def yeu_cau_thong_so(text: str) -> bool:
    """Khach chu dong doi xem thong so ('cho xin thong so chi tiet') - chuyen
    giong ky thuat ngay, khoi cho du 2 thuat ngu."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(r"\b(thong so (chi tiet|day du|ky thuat)|chi tiet thong so|"
                          r"xin thong so|noi thong so|spec)\b", kd))


def hoi_khuyen_mai(text: str) -> bool:
    """Khach hoi may dang giam gia/khuyen mai. Tra loi bang du lieu THAT
    (gia goc vs gia khuyen mai co san trong catalog) - khong doan 'hot',
    khong doan 'noi bat' vi khong co so lieu nao dung sau mot chu do."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(r"\b(khuyen mai|giam gia|dang giam|dang sale|sale|km)\b", kd))


def cau_hoi_cong_suat(text: str) -> bool:
    """Khach hoi KIEN THUC ve cong suat ('gia dinh 5 nguoi mua cong suat bao
    nhieu?', 'phong nay can may HP?') - khac voi nho tu van chon may.

    Phat hien tu demo that: he chi co 2 che do (hoi nguoc / top 3) nen cau hoi
    kien thuc bi tra loi bang... nguyen van cau tu van cu. Can che do thu 3:
    GIAI THICH - template co can cu, khong qua LLM.
    """
    kd = bo_dau(text or "").lower()
    if not re.search(r"\b(cong suat|hp|btu|ngua)\b", kd):
        return False
    return bool(re.search(r"\b(bao nhieu|bn|nao|the nao|sao|can|nen|du)\b", kd))


def nganh_ngoai_pham_vi(text: str) -> str | None:
    """Khach dang hoi nganh khac (khong nhac may lanh) -> tra ten nganh do.

    Co nhac may lanh thi coi nhu dung pham vi (vd 'mua may lanh va tu lanh'
    -> van tu van may lanh, nganh kia tu nhien duoc nhac trong cau tra loi).
    """
    kd = bo_dau(text or "").lower()
    if re.search(r"\b(may lanh|dieu hoa|dhkk|ml)\b", kd):
        return None
    for mau, ten in NGANH_KHAC:
        if re.search(mau, kd):
            return ten
    return None


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
