# -*- coding: utf-8 -*-
"""Trich o nhu cau tu loi khach -> JSON dung khuon.

Day la MOT trong hai cho duy nhat duoc cham LLM. Va cham rat han che:
LLM chi duoc DIEN VAO KHUON, khong duoc tra loi tu do, khong duoc quyet dinh
hoi gi, khong duoc chon san pham. Sai khuon -> loai, thu lai, roi ve duong luat.

Hai duong, dung noi tiep chu khong thay the nhau:
  1. trich_bang_luat  - regex, 0ms, chac chan. Bat duoc phan lon cau mua sam
     thuc te vi chung rat co mau ('duoi 20tr', 'phong 18m2', 'it on').
  2. trich_bang_llm   - vot phan con lai, cau lat leo ('phong be tho thoi',
     'tam 20 chuc'). Chi chay khi duong luat con thieu o BAT BUOC.

Vi sao khong de LLM lam het: luat khong bao gio bia, va mien phi. LLM goi 1 lan
la 0.8-2s + tien + rui ro tra sai khuon. Dung LLM cho phan luat khong voi toi
thi vua re vua nhanh vua chac.
"""
from __future__ import annotations

import json
import re

from backend.app.core.chuan_hoa_tv import bo_dau, chuan_hoa
from backend.app.schemas.nhu_cau import LoaiPhong, ONhuCauMayLanh, UuTien
from backend.app.services.llm import LLM

# Tu khoa uu tien - khop tren ban KHONG DAU.
DAU_HIEU_UU_TIEN = {
    UuTien.TIET_KIEM_DIEN: ("tiet kiem dien", "tkd", "it ton dien", "tiet dien", "inverter"),
    UuTien.DO_ON: ("it on", "em", "yen tinh", "khong on", "on ao"),
    UuTien.LAM_LANH_NHANH: ("lanh nhanh", "lam lanh nhanh", "turbo", "manh"),
    UuTien.DO_BEN: ("ben", "do ben", "dung lau"),
    UuTien.GIA: ("re", "gia re", "tiet kiem tien", "gia tot"),
}

DAU_HIEU_PHONG = {
    LoaiPhong.NGU: ("phong ngu", "ngu"),
    # Quan/van phong/shop: khong gian sinh hoat chung - tinh nhu phong khach
    # (do on it quan trong hon phong ngu). ANH XA loai khong gian, khong sinh so.
    LoaiPhong.KHACH: ("phong khach", "khach", "phong an", "van phong", "quan cafe",
                      "quan ca phe", "quan an", "quan nhau", "cua hang", "shop", "tiem"),
}

HE_THONG = """Bạn là bộ trích xuất thông tin. Nhiệm vụ DUY NHẤT: đọc lời khách và điền vào JSON.
TUYỆT ĐỐI KHÔNG tư vấn, KHÔNG chào hỏi, KHÔNG thêm chữ nào ngoài JSON.
Không suy đoán: khách không nói thì để null.

Khuôn JSON bắt buộc:
{"ngan_sach_max": số nguyên VND hoặc null,
 "dien_tich_m2": số hoặc null,
 "co_nang": true/false/null,
 "loai_phong": "ngu"/"khach"/null,
 "uu_tien": mảng con của ["tiet_kiem_dien","do_on","lam_lanh_nhanh","do_ben","gia"],
 "khu_vuc": chuỗi hoặc null}"""


def trich_bang_luat(text: str) -> ONhuCauMayLanh:
    """Regex tren van ban da chuan hoa. Khong bao gio bia, 0ms."""
    t = chuan_hoa(text)
    kd = bo_dau(t).lower()
    nc = ONhuCauMayLanh()

    # Ngan sach: chuan_hoa da doi '20tr' -> '20000000'
    m = re.search(r"(?:duoi|khoang|tam|toi da|max|<=?|gia)\s*([\d]{6,})", kd)
    if not m:
        # So tien tran: 6+ chu so (500k -> 500000 cung la ngan sach that -
        # bug tim ra khi fuzz: '500k' bi bo qua roi hoi lai ngan sach).
        m = re.search(r"\b([\d]{6,})\b(?!\s*(?:m2|m²|mah|w\b))", kd)
    if m:
        nc.ngan_sach_max = int(m.group(1))

    m = re.search(r"([\d]+(?:[.,][\d]+)?)\s*m²", t)
    if m:
        nc.dien_tich_m2 = float(m.group(1).replace(",", "."))
    if nc.dien_tich_m2 is None:
        # "phong 3x4" / "3m x 4m" -> 12m². PHEP NHAN tu so khach cho, khong
        # phai doan. Chi nhan cap 2 so nho (canh phong hop ly 2-15m), va khong
        # dinh chuoi 3 so kieu "60x65x86" (kich thuoc hoc tu lanh).
        m = re.search(r"(?<![x×\d])(\d{1,2})\s*m?\s*[x×]\s*(\d{1,2})\s*m?\b(?!\s*[x×])", kd)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if 2 <= a <= 15 and 2 <= b <= 15:
                nc.dien_tich_m2 = float(a * b)

    # 'ko/k nang' la viet tat pho bien - thieu la hoi lai thu khach vua noi
    if re.search(r"\b(?:khong|ko|k) (?:co )?nang\b|\brop\b|\bmat\b", kd):
        nc.co_nang = False
    elif re.search(r"\b(co nang|nang chieu|nang truc tiep|huong tay|nang lam)\b", kd):
        nc.co_nang = True

    for lp, tu in DAU_HIEU_PHONG.items():
        if any(re.search(rf"\b{re.escape(x)}\b", kd) for x in tu):
            nc.loai_phong = lp
            break

    for ut, tu in DAU_HIEU_UU_TIEN.items():
        if any(re.search(rf"\b{re.escape(x)}\b", kd) for x in tu):
            nc.uu_tien.append(ut)

    return nc


# Dau hieu khach DOI Y: "neu giam con 15 trieu?", "doi sang phong 25m2",
# "tang len 25tr duoc khong". Khong co dau hieu nay thi o da biet KHONG bao
# gio bi ghi de (chong troi flow). 'ha'/'con' dung mot minh KHONG dua vao:
# 'ha noi' chua 'ha', 'con thu hai' chua 'con' -> ghi de oan.
_MAU_DOI_Y = re.compile(
    r"\b(giam|tang|doi (?:sang|lai|thanh)|thay vi|chi con|neu|xuong con|len)\b"
)


def _khach_doi_y(text: str) -> bool:
    return bool(_MAU_DOI_Y.search(bo_dau(text).lower()))


def _gop(cu: ONhuCauMayLanh, moi: ONhuCauMayLanh, ghi_de: bool = False) -> ONhuCauMayLanh:
    """Gop o moi vao o cu.

    ghi_de=False (mac dinh): o da biet giu nguyen - tranh LLM lat nguoc thong
    tin khach da xac nhan (nguyen nhan kinh dien cua troi flow).
    ghi_de=True: khach DOI Y ("neu giam con 15 trieu?") - o nao khach vua noi
    gia tri moi thi de len. Khong co duong nay thi bot lang le tu van theo
    ngan sach CU = sai ma khong ai biet (bay demo nguy hiem nhat).
    """
    d = cu.model_dump()
    for k, v in moi.model_dump().items():
        if k == "uu_tien":
            d[k] = list(dict.fromkeys((d.get(k) or []) + (v or [])))
        elif v is not None and (ghi_de or d.get(k) is None):
            d[k] = v
    return ONhuCauMayLanh(**d)


def trich_bang_llm(text: str, llm: LLM) -> ONhuCauMayLanh | None:
    """Tra None neu LLM tra rac. Goi la KHONG sap - chi la khong vot them duoc."""
    try:
        raw, _ = llm.sinh_do(HE_THONG, chuan_hoa(text), json_mode=True)
        if not raw:
            return None
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
        return ONhuCauMayLanh(**json.loads(raw))
    except Exception:
        return None      # sai khuon/JSON hong -> bo, duong luat da co ket qua


def _dien_theo_ngu_canh(
    nc: ONhuCauMayLanh, text: str, o_dang_cho: str | None
) -> ONhuCauMayLanh:
    """Hieu cau tra loi CUT LUN theo ngu canh o vua hoi.

    Bot hoi 'co nang khong a?' -> khach go 'khong' - tu nhien nhu tho. Pattern
    chung khong bat duoc (phai 'khong nang' moi khop) -> hoi lap 8 lan nhu
    robot hong (loi tim ra boi bo danh gia). Chi ap dung khi BIET o dang cho -
    'khong' luc dang hoi loai phong thi khong duoc hieu thanh 'khong nang'.
    """
    if not o_dang_cho:
        return nc
    kd = bo_dau(text).lower().strip()
    if o_dang_cho == "co_nang" and nc.co_nang is None:
        if re.search(r"\b(khong|ko|hong)\b", kd):      # kiem 'khong' TRUOC 'co'
            return nc.gan("co_nang", False)            # ('khong co nang' chua ca hai)
        if re.search(r"\b(co|u|vang|dung|yes)\b", kd):
            return nc.gan("co_nang", True)
    if o_dang_cho == "dien_tich_m2" and nc.dien_tich_m2 is None:
        if re.fullmatch(r"[\d.,]+", kd):               # go moi so tran: '18'
            return nc.gan("dien_tich_m2", float(kd.replace(",", ".")))
    return nc


def trich(
    text: str,
    llm: LLM,
    o_cu: ONhuCauMayLanh | None = None,
    o_dang_cho: str | None = None,
) -> ONhuCauMayLanh:
    """Ham chinh. Luat truoc, LLM chi vot khi luat con thieu o BAT BUOC.

    o_dang_cho: ten o ma bot vua hoi o luot truoc (tu may trang thai) - de
    hieu cau tra loi cut lun 'co'/'khong'/'18'.
    """
    nc = _gop(o_cu or ONhuCauMayLanh(), trich_bang_luat(text), ghi_de=_khach_doi_y(text))
    nc = _dien_theo_ngu_canh(nc, text, o_dang_cho)
    if nc.thieu_bat_buoc():
        them = trich_bang_llm(text, llm)
        if them is not None:
            nc = _gop(nc, them)      # duong LLM khong bao gio duoc ghi de
    return nc
