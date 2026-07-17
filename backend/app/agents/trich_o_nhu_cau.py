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
    LoaiPhong.KHACH: ("phong khach", "khach", "phong an"),
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
        m = re.search(r"\b([\d]{7,})\b", kd)          # so tien tran trong cau
    if m:
        nc.ngan_sach_max = int(m.group(1))

    m = re.search(r"([\d]+(?:[.,][\d]+)?)\s*m²", t)
    if m:
        nc.dien_tich_m2 = float(m.group(1).replace(",", "."))

    if re.search(r"\b(co nang|nang chieu|nang truc tiep|huong tay|nang lam)\b", kd):
        nc.co_nang = True
    elif re.search(r"\b(khong nang|khong co nang|rop|mat)\b", kd):
        nc.co_nang = False

    for lp, tu in DAU_HIEU_PHONG.items():
        if any(re.search(rf"\b{re.escape(x)}\b", kd) for x in tu):
            nc.loai_phong = lp
            break

    for ut, tu in DAU_HIEU_UU_TIEN.items():
        if any(re.search(rf"\b{re.escape(x)}\b", kd) for x in tu):
            nc.uu_tien.append(ut)

    return nc


def _gop(cu: ONhuCauMayLanh, moi: ONhuCauMayLanh) -> ONhuCauMayLanh:
    """Gop o moi vao o cu. O da biet KHONG bi ghi de - tranh LLM lat nguoc
    thong tin khach da xac nhan o luot truoc (nguyen nhan kinh dien cua troi flow).
    """
    d = cu.model_dump()
    for k, v in moi.model_dump().items():
        if k == "uu_tien":
            d[k] = list(dict.fromkeys((d.get(k) or []) + (v or [])))
        elif d.get(k) is None and v is not None:
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


def trich(text: str, llm: LLM, o_cu: ONhuCauMayLanh | None = None) -> ONhuCauMayLanh:
    """Ham chinh. Luat truoc, LLM chi vot khi luat con thieu o BAT BUOC."""
    nc = _gop(o_cu or ONhuCauMayLanh(), trich_bang_luat(text))
    if nc.thieu_bat_buoc():
        them = trich_bang_llm(text, llm)
        if them is not None:
            nc = _gop(nc, them)
    return nc
