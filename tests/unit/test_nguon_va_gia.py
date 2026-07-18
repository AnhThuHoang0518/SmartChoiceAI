# -*- coding: utf-8 -*-
"""Hoi quy cho TC-138: gia/nguon khong duoc tao cam giac cap nhat gia."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from backend.app.services.catalog import tai_catalog
from backend.app.guardrails.hau_kiem import hau_kiem_khang_dinh
from backend.app.schemas.ket_qua import BangKetQua, Nguon, UngVien
from backend.app.services.parse_dmx import la_khong_ro, la_phu_dinh, parse_gia


def test_gia_khuyen_mai_thap_hon_gia_goc_duoc_giu_nguyen():
    assert parse_gia("10.000.000", "8.000.000") == (8_000_000, 10_000_000)


def test_gia_khuyen_mai_cao_hon_gia_goc_khong_duoc_quang_cao():
    # Du lieu nguon bat thuong: khong coi 12 trieu la gia khuyen mai.
    assert parse_gia("10.000.000", "12.000.000") == (10_000_000, 10_000_000)


def test_thieu_gia_khong_bao_gio_bi_coi_la_gia_0():
    assert parse_gia(None, None) == (None, None)


def test_phan_biet_phu_dinh_that_voi_unknown():
    assert la_phu_dinh("Không") is True
    assert la_khong_ro("Không") is False
    assert la_khong_ro("Hãng không công bố") is True
    assert la_khong_ro("Đang cập nhật") is True


def test_catalog_chan_gia_bat_thuong_va_ghi_dung_nguon_tap_tin(tmp_path):
    p = tmp_path / "may_lanh.csv"
    p.write_text(
        "ma_sp,ten,hang,pham_vi_min,pham_vi_max,gia,gia_goc,do_on_db,cspf,"
        "sao,inverter,lam_lanh_nhanh,loai_may\n"
        "ML-1,May lanh A,Hang A,10,20,12000000,10000000,30,5.2,5,1,1,1 chieu\n",
        encoding="utf-8",
    )
    moc = datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc).timestamp()
    os.utime(p, (moc, moc))

    sp = tai_catalog(p)[0]

    assert (sp.gia, sp.gia_goc) == (10_000_000, 10_000_000)
    assert sp.co_khuyen_mai() is False
    assert sp.nguon["gia"].nguon == "catalog:Giá bán"
    assert "price_api" not in sp.nguon["gia"].nguon
    assert datetime.fromisoformat(sp.nguon["gia"].lay_luc).year == 2020


def _bang_voi_nguon(*nguon: Nguon) -> BangKetQua:
    return BangKetQua(top3=[UngVien(
        ma_sp="A", ten="Máy A", gia=10_000_000, diem=1.0, nguon=list(nguon)
    )])


def _n(truong: str, gia_tri: str, ten_nguon: str = "catalog:Thông số") -> Nguon:
    return Nguon(truong=truong, gia_tri=gia_tri, nguon=ten_nguon,
                 lay_luc="2020-01-01T00:00:00+00:00", ma_sp="A")


def test_claim_dinh_tinh_khong_co_evidence_bi_chan():
    bang = _bang_voi_nguon(_n("gia", "10000000", "catalog:Giá bán"))
    loi = hau_kiem_khang_dinh("Máy này chạy êm, bền bỉ và diệt khuẩn tốt.", bang)
    assert any("chạy êm" in x for x in loi)
    assert any("độ bền" in x for x in loi)
    assert any("khử/diệt khuẩn" in x for x in loi)


def test_claim_dinh_tinh_co_evidence_duoc_phep():
    bang = _bang_voi_nguon(
        _n("do_on_db", "28", "catalog:Độ ồn"),
        _n("cong_nghe", "Lọc bụi và kháng khuẩn", "catalog:Công nghệ"),
    )
    assert hau_kiem_khang_dinh(
        "Máy vận hành êm, có lọc bụi và kháng khuẩn.", bang
    ) == []


def test_field_phu_dinh_khong_duoc_bien_thanh_loi_ich():
    bang = _bang_voi_nguon(
        _n("lam_lanh_nhanh", "Không ghi nhận", "catalog:Công nghệ làm lạnh")
    )
    assert hau_kiem_khang_dinh("Máy làm lạnh nhanh.", bang)
