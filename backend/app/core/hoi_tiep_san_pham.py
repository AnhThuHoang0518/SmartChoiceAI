# -*- coding: utf-8 -*-
"""Hoi tiep co nguon: 'con thu hai co thong so X khong?'.

Khong goi LLM, khong doc lai catalog va khong chay lai ranking. San pham duoc
resolve theo top gan nhat; gia tri chi doc tu ``nguon`` da luu cua dung card.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from backend.app.core.chuan_hoa_tv import bo_dau
from backend.app.core.nhan_truong import dinh_dang


@dataclass(frozen=True)
class TruongHoi:
    nhan: str
    cac_truong: tuple[str, ...]


_SO_THU_TU = {
    "1": 0, "mot": 0, "nhat": 0, "dau": 0, "dau tien": 0,
    "2": 1, "hai": 1,
    "3": 2, "ba": 2,
}


_TRUONG_HOI: tuple[tuple[str, TruongHoi], ...] = (
    (r"\bbang dieu khien\b", TruongHoi("bảng điều khiển", ("bang_dieu_khien",))),
    (r"\bbao hanh\b", TruongHoi("bảo hành của sản phẩm", ("bao_hanh_dc_nam",))),
    (r"\bgia goc\b", TruongHoi("giá gốc", ("gia_goc",))),
    (r"\b(?:gia|bao nhieu tien)\b", TruongHoi("giá", ("gia",))),
    (r"\b(?:qua tang|khuyen mai)\b", TruongHoi("quà tặng", ("qua",))),
    (r"\b(?:kich thuoc|rong dai cao)\b", TruongHoi(
        "kích thước", ("ngang_cm", "sau_cm", "cao_cm")
    )),
    (r"\bngang\b", TruongHoi("chiều ngang", ("ngang_cm",))),
    (r"\b(?:sau|do sau)\b", TruongHoi("chiều sâu", ("sau_cm",))),
    (r"\bcao\b", TruongHoi("chiều cao", ("cao_cm",))),
    (r"\b(?:do on|chay em|it on)\b", TruongHoi("độ ồn", ("do_on_db",))),
    (r"\b(?:dien nang|ton dien|tiet kiem dien)\b", TruongHoi(
        "điện năng", ("dien_kwh_nam", "dien_kwh_ngay", "dien_wh_kg", "cspf")
    )),
    (r"\bcong suat\b", TruongHoi("công suất", ("cong_suat_w", "dien_w"))),
    (r"\bdung tich\b", TruongHoi("dung tích", ("dung_tich_lit", "binh_lit"))),
    (r"\bpin\b", TruongHoi("pin", ("pin_ngay", "pin_gio", "pin_mah"))),
    (r"\bram\b", TruongHoi("RAM", ("ram_gb",))),
    (r"\b(?:bo nho|luu tru|o cung|ssd)\b", TruongHoi(
        "bộ nhớ", ("luu_tru_gb", "ssd_gb")
    )),
    (r"\bsim\b", TruongHoi("SIM", ("sim",))),
    (r"\bket noi\b", TruongHoi("kết nối", ("ket_noi",))),
    (r"\btam nen\b", TruongHoi("tấm nền", ("tam_nen",))),
    (r"\bdo phan giai\b", TruongHoi("độ phân giải", ("phan_giai",))),
    (r"\bkhang nuoc\b", TruongHoi("kháng nước", ("khang_nuoc",))),
    (r"\bnghe goi\b", TruongHoi("nghe gọi", ("nghe_goi",))),
    (r"\b(?:loai|kieu)\b", TruongHoi("loại sản phẩm", ("loai", "kieu_dang"))),
)


def chi_so_san_pham(text: str) -> int | None:
    kd = bo_dau(text or "").lower()
    mau = (
        r"\b(?:con|may|cai|mau|san pham|sp)\s*"
        r"(?:so\s*|thu\s*)?(dau tien|mot|nhat|hai|ba|[123])\b"
    )
    if not (m := re.search(mau, kd)):
        return None
    return _SO_THU_TU.get(m.group(1))


def _truong_duoc_hoi(text: str) -> TruongHoi | None:
    kd = bo_dau(text or "").lower()
    for mau, spec in _TRUONG_HOI:
        if re.search(mau, kd):
            return spec
    # Cau noi ro dang hoi mot thong so/chi so ma schema khong biet.
    if re.search(r"\b(?:thong so|chi so|truong du lieu)\b", kd):
        return TruongHoi("thông số được hỏi", ())
    return None


def _co_gia_tri(n: dict) -> bool:
    return str(n.get("gia_tri", "")).strip().lower() not in {
        "", "none", "null", "nan", "hang khong cong bo", "hãng không công bố",
    }


def tra_loi_truong_san_pham(text: str, top3: list[dict]) -> dict | None:
    """Tra payload cho API, None neu khong phai hoi 'san pham thu N + field'."""
    chi_so = chi_so_san_pham(text)
    spec = _truong_duoc_hoi(text)
    if chi_so is None or spec is None or not top3:
        return None

    if chi_so >= len(top3):
        return {
            "loai": "thieu_du_lieu",
            "text": (f"Dạ danh sách vừa rồi chỉ có {len(top3)} sản phẩm nên "
                     f"không có sản phẩm thứ {chi_so + 1} để đối chiếu ạ."),
            "chi_so": chi_so,
            "truong": list(spec.cac_truong),
        }

    san_pham = top3[chi_so]
    theo_truong = {}
    for n in san_pham.get("nguon", []):
        truong = n.get("truong")
        if truong in spec.cac_truong and _co_gia_tri(n):
            theo_truong.setdefault(truong, n)

    if not theo_truong:
        return {
            "loai": "thieu_du_lieu",
            "text": (f"Dạ em đang đối chiếu **{san_pham.get('ten', 'sản phẩm này')}** "
                     f"(sản phẩm thứ {chi_so + 1}). Dữ liệu nguồn hiện chưa có "
                     f"trường {spec.nhan}, nên em chưa thể xác nhận và không "
                     "đoán từ hãng hoặc tên máy ạ."),
            "chi_so": chi_so,
            "truong": list(spec.cac_truong),
        }

    dong = []
    co_suy_luan = False
    for truong in spec.cac_truong:
        if (n := theo_truong.get(truong)) is None:
            continue
        nhan, gia_tri = dinh_dang(truong, str(n["gia_tri"]))
        dong.append(f"**{nhan}:** {gia_tri}")
        co_suy_luan = co_suy_luan or bool(n.get("suy_luan"))
    canh_bao = (
        " Đây là trường suy luận từ mô tả, không phải trường số chính thức ạ."
        if co_suy_luan else ""
    )
    return {
        "loai": "tra_loi_san_pham",
        "text": (f"Dạ **{san_pham.get('ten', 'sản phẩm này')}** là sản phẩm thứ "
                 f"{chi_so + 1} trong danh sách vừa rồi. " + " · ".join(dong)
                 + f".{canh_bao}"),
        "chi_so": chi_so,
        "truong": list(theo_truong),
    }
