# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from pathlib import Path

from backend.app.api.chat import _nhan_manh_uu_tien_may_lanh
from backend.app.nganh.tu_lanh import (
    TuLanh,
    bang_thanh_chu_tu_lanh,
    trich_tu_lanh,
    xep_hang_tu_lanh,
)
from backend.app.schemas.ket_qua import Nguon, UngVien
from backend.app.schemas.nhu_cau import UuTien


def _nguon(truong: str, gia_tri, ma: str) -> Nguon:
    return Nguon(
        truong=truong,
        gia_tri=str(gia_tri),
        nguon=f"catalog:{truong}",
        lay_luc=datetime.now(timezone.utc).isoformat(),
        ma_sp=ma,
    )


def _tu_lanh(ma: str, ten: str, ngang: float | None) -> TuLanh:
    nguon = {
        "gia": _nguon("gia", 8_000_000, ma),
        "nguoi_phu_hop": _nguon("nguoi_phu_hop", "3-5 người", ma),
    }
    if ngang is not None:
        nguon["ngang_cm"] = _nguon("ngang_cm", ngang, ma)
    return TuLanh(
        ma_sp=ma,
        ten=ten,
        hang="Hang mau",
        nguoi_min=3,
        nguoi_max=5,
        ngang_cm=ngang,
        gia=8_000_000,
        gia_goc=8_000_000,
        nguon=nguon,
    )


def test_tu_lanh_rong_75_cm_loc_va_noi_ro_kich_thuoc():
    nc = trich_tu_lanh(
        "Nhà 4 người, tầm 12 triệu. Bếp tôi chỉ rộng 75 cm, tìm tủ lạnh đặt vừa."
    )
    assert nc.ngang_cm == 75

    bang, thieu = xep_hang_tu_lanh(
        [_tu_lanh("fit", "Tủ vừa", 70), _tu_lanh("wide", "Tủ rộng", 80),
         _tu_lanh("missing", "Tủ thiếu số", None)],
        nc,
    )
    assert [u.ma_sp for u in bang.top3] == ["fit"]
    assert thieu == 1
    assert "kích thước ngang 70 cm" in bang_thanh_chu_tu_lanh(bang, nc, thieu, "binh_dan")


def test_tieu_chi_chay_em_duoc_noi_thang_khi_chi_co_mot_may():
    may = UngVien(
        ma_sp="ml1",
        ten="Máy lạnh mẫu",
        gia=9_990_000,
        diem=1,
        nguon=[_nguon("do_on_db", 18, "ml1")],
    )
    text = _nhan_manh_uu_tien_may_lanh(may, [UuTien.DO_ON])
    assert "đúng tiêu chí" in text
    assert "18 dB" in text


def test_ui_khong_hien_thong_ke_debug_cho_khach():
    html = Path("frontend/chat/index.html").read_text(encoding="utf-8")
    assert "chạm LLM:" not in html
    assert "<span>lọc " not in html
