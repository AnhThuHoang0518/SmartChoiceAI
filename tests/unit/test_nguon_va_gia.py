# -*- coding: utf-8 -*-
"""Hoi quy cho TC-138: gia/nguon khong duoc tao cam giac cap nhat gia."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from backend.app.services.catalog import tai_catalog
from backend.app.services.parse_dmx import parse_gia


def test_gia_khuyen_mai_thap_hon_gia_goc_duoc_giu_nguyen():
    assert parse_gia("10.000.000", "8.000.000") == (8_000_000, 10_000_000)


def test_gia_khuyen_mai_cao_hon_gia_goc_khong_duoc_quang_cao():
    # Du lieu nguon bat thuong: khong coi 12 trieu la gia khuyen mai.
    assert parse_gia("10.000.000", "12.000.000") == (10_000_000, 10_000_000)


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
