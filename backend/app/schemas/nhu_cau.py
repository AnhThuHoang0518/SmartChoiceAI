# -*- coding: utf-8 -*-
"""HOP DONG 1 - O nhu cau (slot) nganh hang may lanh.

Day la khuon DUY NHAT ma LLM duoc phep tra ve o buoc trich o nhu cau.
Sai khuon -> loai, trich lai. Moi nhanh code khac chi doc/ghi qua khuon nay.

Vi sao tach ra file rieng: 3 nhanh (du lieu / quyet dinh / LLM) chay song song
duoc la nho chot khuon nay TRUOC. Doi khuon = pha vo ca 3 nhanh.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LoaiPhong(str, Enum):
    NGU = "ngu"
    KHACH = "khach"


class UuTien(str, Enum):
    TIET_KIEM_DIEN = "tiet_kiem_dien"
    DO_ON = "do_on"
    LAM_LANH_NHANH = "lam_lanh_nhanh"
    DO_BEN = "do_ben"
    GIA = "gia"


# O bat buoc phai co truoc khi dam xep hang. Thieu -> khong the tu van.
O_BAT_BUOC: tuple[str, ...] = ("ngan_sach_max", "dien_tich_m2")

# O co the hoi nguoc. Thu tu trong tuple nay KHONG co y nghia uu tien - o nao
# dang hoi truoc la do GIA TRI THONG TIN quyet dinh, khong phai do ai xep san.
O_CO_THE_HOI: tuple[str, ...] = (
    "ngan_sach_max",
    "dien_tich_m2",
    "co_nang",
    "loai_phong",
    "khu_vuc",
)

# Tap gia tri de mo phong khi do gia tri thong tin: "neu o nay dien X thi top 3
# co doi khong?". Chi o ROI RAC mo phong duoc. O lien tuc (ngan sach, dien tich)
# khong co trong day - nhung chung deu la O_BAT_BUOC nen luon phai hoi truoc.
GIA_TRI_THU: dict[str, list] = {
    "co_nang": [True, False],
    "loai_phong": [LoaiPhong.NGU, LoaiPhong.KHACH],
    "khu_vuc": ["hn", "hcm", "dn"],
}


class ONhuCauMayLanh(BaseModel):
    """Phieu nhu cau cua khach. None = chua biet, KHONG phai gia tri mac dinh."""

    ngan_sach_max: int | None = Field(None, description="VND, tran chi tieu")
    dien_tich_m2: float | None = Field(None, description="Dien tich phong")
    co_nang: bool | None = Field(None, description="Nang chieu truc tiep?")
    loai_phong: LoaiPhong | None = None
    uu_tien: list[UuTien] = Field(default_factory=list)
    khu_vuc: str | None = Field(None, description="Tinh/TP - de tra ton kho")
    hang: str | None = Field(None, description="Loc theo hang khach neu (doi chieu catalog)")
    hang_tru: str | None = Field(None, description="Hang khach KHONG muon ('khong phai LG') -> loai")
    can_inverter: bool | None = Field(None, description="True=chi Inverter, False=chi mono, None=khong rang buoc")

    def con_trong(self) -> list[str]:
        """O nao chua biet va co the hoi nguoc."""
        return [o for o in O_CO_THE_HOI if getattr(self, o) is None]

    def thieu_bat_buoc(self) -> list[str]:
        return [o for o in O_BAT_BUOC if getattr(self, o) is None]

    def du_de_xep_hang(self) -> bool:
        return not self.thieu_bat_buoc()

    def gan(self, ten_o: str, gia_tri) -> "ONhuCauMayLanh":
        """Tra ban sao co o duoc dien - dung khi mo phong gia tri thong tin."""
        return self.model_copy(update={ten_o: gia_tri})
