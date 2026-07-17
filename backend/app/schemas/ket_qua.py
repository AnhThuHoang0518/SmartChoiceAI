# -*- coding: utf-8 -*-
"""HOP DONG 2 - Bang ket qua top 3.

Day la thu DUY NHAT ma LLM viet-lai duoc nhin thay. No khong co quyen tra
catalog, khong biet san pham nao khac ton tai.

Moi con so o day deu keo theo Nguon -> hau kiem doi chieu nguoc duoc, va UI
gan badge bam ra nguon duoc. Khong co truong nao "tran" khong nguon.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Nguon(BaseModel):
    """Dau vet cua MOT truong du lieu. Thieu cai nay = khong duoc khang dinh."""

    truong: str = Field(description="vd: gia, do_on_db, ton_kho")
    gia_tri: str = Field(description="Gia tri da chuan hoa, dang chuoi de log")
    nguon: str = Field(description="vd: price_api, catalog.csv, mo_ta_san_pham")
    lay_luc: str = Field(description="ISO 8601")
    ma_sp: str
    suy_luan: bool = Field(
        False,
        description="True = truong nay trich tu mo ta chu khong phai field chinh "
        "thuc. CHI duoc goi y kem canh bao, CAM dung de khang dinh.",
    )


class TrucSoSanh(BaseModel):
    """Mot truc so sanh giua 2 san pham. Code sinh ra - LLM KHONG tu nghi."""

    truc: str = Field(description="vd: do on, dien nang, gia")
    cua_minh: str = Field(description="vd: 26 dB")
    doi_thu: str = Field(description="vd: May B 29 dB")


def dong_so_sanh(x: "TrucSoSanh", la_hon: bool) -> str:
    """Dien dat 1 truc trade-off thanh cau tu nhien cho LLM/ban du phong.

    Truoc day serialize "HƠN về giá / KÉM về giá" -> LLM nhai lai nguyen van
    ("Kém về giá vì đắt hơn") nghe nhu may dich (thay tren demo that). Truc
    'giá' co tu rieng (rẻ/đắt), truc khac dung 'nhỉnh hơn / chịu thiệt'.
    """
    if x.truc == "giá":
        dau = "Rẻ hơn" if la_hon else "Đắt hơn"
        return f"   {dau}: {x.cua_minh} (so với {x.doi_thu})"
    dau = f"Nhỉnh hơn về {x.truc}" if la_hon else f"Chịu thiệt về {x.truc}"
    return f"   {dau}: {x.cua_minh} (so với {x.doi_thu})"


class UngVien(BaseModel):
    ma_sp: str
    ten: str
    gia: int
    diem: float = Field(description="Diem cham 0-1, de xep hang")
    hon: list[TrucSoSanh] = Field(default_factory=list, description="Duoc gi")
    kem: list[TrucSoSanh] = Field(default_factory=list, description="Mat gi")
    nguon: list[Nguon] = Field(default_factory=list)


class LyDoLoai(BaseModel):
    """San pham bi loc cung loai bo - neu chu dong de khach khoi thac mac.

    Chon cai NOI BAT nhat (re nhat / hay duoc quang cao) chu khong phai ngau nhien.
    """

    ma_sp: str
    ten: str
    ly_do: str = Field(description="Ma ly do, vd: cong_suat, ngan_sach, het_hang")
    chi_tiet: str = Field(description="Loi giai thich cho khach, vd: 1.5HP < 2.0HP toi thieu")


class BangKetQua(BaseModel):
    top3: list[UngVien]
    loai_noi_bat: LyDoLoai | None = None
    dien_tich_hieu_dung_m2: float | None = Field(
        None, description="Dien tich quy doi theo tai nhiet (nang -> nhan he so)"
    )
    tong_truoc_loc: int = 0
    con_lai_sau_loc: int = 0

    def moi_nguon(self) -> list[Nguon]:
        """Gop nguon cua ca top3 - hau kiem doi chieu vao day."""
        return [n for uv in self.top3 for n in uv.nguon]


class CauHoiNguoc(BaseModel):
    """Nhanh 'chua du o' tra ve cai nay. KHONG qua LLM."""

    o_hoi: str = Field(description="Ten o dang hoi, vd: co_nang")
    cau_hoi: str = Field(description="Template cung tu configs")
    diem_gia_tri: float = Field(description="Diem gia tri thong tin, de log/giai trinh")
