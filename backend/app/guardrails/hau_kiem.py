# -*- coding: utf-8 -*-
"""CHOT CHAN - quet moi con so LLM viet ra, doi chieu nguoc bang ket qua.

De bai cham 10% cho "Tinh dung du lieu & chong hallucination", va liet ke thang
vao muc CAM: "bia gia/ton kho/khuyen mai". Prompt bao LLM "dung bia" la loi
khuyen, khong phai co che. Day moi la co che.

BAI HOC (ban dau viet sai, da vet):
So phai kiem THEO DON VI, khong duoc gop chung mot ro. Ban dau tap hop le la
mot set so tran -> khach noi "phong 18m2" the la so 18 thanh hop le, LLM bia
"em 18 dB" lien lot qua. Gio moi loai don vi co ro rieng: 18 hop le o ro m2
nhung khong hop le o ro dB.

Hai cai bay con lai:
  1. Chi kiem so CO DON VI. So tran ("3 may", "top 3") la dem, khong phai so
     lieu san pham - bat het thi bao dong gia lien tuc.
  2. Phai cho phep so SUY RA: "re hon 1,2 trieu" khong nam trong catalog ma la
     hieu 2 gia. Khong cho thi LLM khong noi duoc trade-off bang tien - ma do
     lai la thu an diem nhat.
"""
from __future__ import annotations

import re

from backend.app.schemas.ket_qua import BangKetQua

# don_vi -> (regex, he so quy doi)
MAU_SO: dict[str, list[tuple[str, float]]] = {
    "tien": [
        (r"([\d.,]+)\s*(?:triệu|tr)\b", 1_000_000.0),
        (r"([\d.,]+)\s*(?:nghìn|k)\b", 1_000.0),
        (r"([\d.,]+)\s*(?:đồng|đ|vnd)\b", 1.0),
    ],
    "db": [(r"([\d.,]+)\s*dB\b", 1.0)],
    "cspf": [(r"CSPF\s*([\d.,]+)", 1.0)],
    "sao": [(r"([\d.,]+)\s*sao\b", 1.0)],
    "m2": [(r"([\d.,]+)\s*m²", 1.0)],
    "phan_tram": [(r"([\d.,]+)\s*%", 1.0)],
    # Nganh tu lanh (moi don vi mot ro rieng - bai hoc "18 dB lot vi 18m2")
    "lit": [(r"([\d.,]+)\s*(?:lít|lit|L)\b", 1.0)],
    "kwh": [(r"([\d.,]+)\s*kWh", 1.0)],
    "cm": [(r"([\d.,]+)\s*cm\b", 1.0)],
    "nguoi": [(r"([\d.,]+)\s*người", 1.0)],
    # Nhom gia dung (may giat/say) - moi don vi mot ro rieng nhu moi khi
    "kg": [(r"([\d.,]+)\s*kg", 1.0)],
    "vong": [(r"([\d.,]+)\s*vòng", 1.0)],
    "whkg": [(r"([\d.,]+)\s*Wh/kg", 1.0)],
    "w": [(r"([\d.,]+)\s*W\b(?!h)", 1.0)],
    "doc": [(r"([\d.,]+)\s*°C", 1.0)],
    "nam": [(r"([\d.,]+)\s*năm", 1.0)],
    "bua": [(r"([\d.,]+)\s*bữa", 1.0)],
    "bo": [(r"([\d.,]+)\s*bộ", 1.0)],
    # Nhom dien tu
    "inch": [(r"([\d.,]+)\s*inch", 1.0)],
    "gb": [(r"([\d.,]+)\s*GB", 1.0)],
    "mah": [(r"([\d.,]+)\s*mAh", 1.0)],
    "gam": [(r"([\d.,]+)\s*(?:gam|gram|g)\b", 1.0)],
    "ngay": [(r"([\d.,]+)\s*ngày", 1.0)],
    "ms": [(r"([\d.,]+)\s*ms\b", 1.0)],
    "nit": [(r"([\d.,]+)\s*(?:nit|cd/m)", 1.0)],
    "trang": [(r"([\d.,]+)\s*trang", 1.0)],
    "m": [(r"([\d.,]+)\s*m\b(?!s|Ah|²)", 1.0)],
    "to": [(r"([\d.,]+)\s*tờ", 1.0)],
    "gio": [(r"([\d.,]+)\s*(?:giờ|tiếng)", 1.0)],
}

# truong trong Nguon -> ro don vi (dung chung moi nganh)
_TRUONG_RO = {
    "gia": "tien", "gia_goc": "tien",
    "do_on_db": "db", "cspf": "cspf", "sao": "sao",
    "dung_tich_lit": "lit", "dien_kwh_nam": "kwh",
    "ngang_cm": "cm", "cao_cm": "cm", "sau_cm": "cm",
    "so_nguoi": "nguoi",
    "tai_kg": "kg", "vat_vong": "vong", "dien_wh_kg": "whkg", "dien_w": "w",
    "nhiet_toi_da_c": "doc", "bao_hanh_dc_nam": "nam",
    "nguoi_min": "nguoi", "nguoi_max": "nguoi",
    "bua_min": "bua", "bua_max": "bua", "bo_chau_au": "bo",
    "nuoc_lit": "lit", "dung_tich_min": "lit",
    "dien_kwh_ngay": "kwh", "cong_suat_w": "w", "binh_lit": "lit",
    "ngan_da_lit": "lit", "phu_mau_pct": "phan_tram", "khay_to": "to",
    "cong_suat_thang": "trang",
    "man_inch": "inch", "ram_gb": "gb", "luu_tru_gb": "gb", "ssd_gb": "gb",
    "pin_mah": "mah", "nang_g": "gam", "pin_ngay": "ngay",
    "dap_ung_ms": "ms", "do_sang_nit": "nit", "toc_do_trang": "trang",
    "khoang_cach_m": "m", "pin_gio": "gio",
}

# thuoc tinh trong o nhu cau -> ro (loi khach noi cung la nguon su that)
_NHU_CAU_RO = {
    "dien_tich_m2": "m2", "ngan_sach_max": "tien", "so_nguoi": "nguoi",
    "ngang_cm": "cm", "cao_cm": "cm", "sau_cm": "cm",
}


def _so(s: str) -> float | None:
    """'17,9' -> 17.9 | '17.890.000' -> 17890000. Tieng Viet dung ',' lam thap phan."""
    t = s.strip()
    if re.fullmatch(r"[\d]{1,3}(\.[\d]{3})+", t):
        return float(t.replace(".", ""))
    t = t.replace(".", "").replace(",", ".") if "," in t else t
    try:
        return float(t)
    except ValueError:
        return None


def trich_so(text: str) -> list[tuple[str, str, float]]:
    """Tra [(nguyen van, don vi, gia tri)] cho moi so CO DON VI."""
    ra = []
    for don_vi, maus in MAU_SO.items():
        for mau, he_so in maus:
            for m in re.finditer(mau, text, re.I):
                # rstrip dau cau: 'CSPF 5.32,' tung bi bat oan thanh 532
                # (dau phay cuoi lam _so hieu nham kieu thap phan) - chan oan
                # la ton 1 luot viet lai 4-6s voi LLM that.
                v = _so(m.group(1).rstrip(".,"))
                if v is not None:
                    ra.append((m.group(0).strip(), don_vi, v * he_so))
    return ra


def tap_hop_le(bang: BangKetQua, nhu_cau=None) -> dict[str, set[float]]:
    """Ro so hop le TUNG don vi. Ngoai ro cua don vi do = bia.

    Co nhu_cau vao day: loi khach cung la nguon su that. Khach bao "phong 18m2,
    duoi 20 trieu" thi LLM nhac lai la dung - chan la duong tinh gia, ma duong
    tinh gia con nguy hon bo lot: no day ca cau tra loi that ve ban du phong.
    """
    ro: dict[str, set[float]] = {k: set() for k in MAU_SO}

    gia = []
    for u in bang.top3:
        ro["tien"].add(float(u.gia))
        gia.append(float(u.gia))
        for n in u.nguon:
            v = _so(str(n.gia_tri))
            ten_ro = _TRUONG_RO.get(n.truong)
            if ten_ro and v is not None:
                ro[ten_ro].add(v)
            elif n.truong in ("pham_vi", "nguoi_phu_hop"):
                # dang khoang '15.0-20.0m²' / '3-4 nguoi' -> tach 2 dau
                ro_khoang = "m2" if n.truong == "pham_vi" else "nguoi"
                for x in re.findall(r"[\d.]+", str(n.gia_tri)):
                    if (v2 := _so(x)) is not None:
                        ro[ro_khoang].add(v2)

    # So SUY RA: chenh gia doi mot ("re hon X trieu").
    for i in range(len(gia)):
        for j in range(len(gia)):
            if i != j:
                ro["tien"].add(abs(gia[i] - gia[j]))

    # Muc giam khuyen mai ("dang giam 1,3 trieu") = gia_goc - gia ban.
    for u in bang.top3:
        for n in u.nguon:
            if n.truong == "gia_goc" and (v := _so(str(n.gia_tri))):
                ro["tien"].add(abs(v - float(u.gia)))

    if bang.dien_tich_hieu_dung_m2:
        ro["m2"].add(float(bang.dien_tich_hieu_dung_m2))

    if nhu_cau is not None:
        for thuoc_tinh, ten_ro in _NHU_CAU_RO.items():
            if x := getattr(nhu_cau, thuoc_tinh, None):
                ro[ten_ro].add(float(x))

    # 'phan_tram' co chu y de RONG: catalog khong co truong % nao. Moi con so %
    # deu la LLM tu nghi ra ("tiet kiem 40% dien") -> chan sach.
    return {k: {v for v in s if v} for k, s in ro.items()}


def hau_kiem(
    text: str, bang: BangKetQua, nhu_cau=None, dung_sai: float = 0.005
) -> list[str]:
    """Tra danh sach loi. Rong = dat.

    dung_sai tuong doi vi LLM lam tron cho de doc: 14.690.000 -> '14,7 trieu'
    lech 0,07% -> phai cho qua, khong thi no doc so nguyen ban nghe nhu robot.
    """
    ro = tap_hop_le(bang, nhu_cau)
    loi = []
    for nguyen_van, don_vi, v in trich_so(text):
        hop_le = ro.get(don_vi, set())
        if any(abs(v - h) <= max(dung_sai * max(abs(h), 1.0), 0.05) for h in hop_le):
            continue
        loi.append(f'"{nguyen_van}" không khớp dữ liệu nào ({don_vi}) trong bảng kết quả')
    return loi


def ban_du_phong(bang: BangKetQua, cau_mau: str) -> str:
    """Dung khi LLM bi chan qua so lan cho phep.

    Kho khan nhung MOI SO deu tu bang. Tha tra loi cung nhac con hon bia - de
    bai ghi ro "khong bia du lieu neu API/catalog khong co".
    """
    from backend.app.core.nhan_truong import tien_chu
    ds = ", ".join(f"{u.ten} ({tien_chu(u.gia)})" for u in bang.top3)
    return cau_mau.format(dien_tich_m2=bang.dien_tich_hieu_dung_m2 or "?", danh_sach=ds)
