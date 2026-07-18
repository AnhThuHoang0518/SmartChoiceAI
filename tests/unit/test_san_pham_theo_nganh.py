# -*- coding: utf-8 -*-
"""Endpoint /api/san-pham cho trang danh muc landing: san pham THAT tu catalog,
KHONG mock. Nganh co data -> tra san pham + danh sach hang; nganh khong co data
-> rong (UI hien 'dang cap nhat'). Loc hang/gia + sap xep chay tren data that."""
from backend.app.api.chat import san_pham_theo_nganh as f


def test_nganh_co_data_tra_san_pham_that():
    for slug in ["may-lanh", "tu-lanh", "may-giat", "may-say"]:
        r = f(nganh=slug)
        assert r["ten"] and r["tong"] > 0, slug
        assert r["san_pham"], slug
        sp = r["san_pham"][0]
        # moi con so co that: gia > 0, gia_goc >= gia, co ten + hang
        assert sp["gia"] > 0 and sp["gia_goc"] >= sp["gia"]
        assert sp["ten"] and sp["hang"]
        assert sp["hang"] in r["hang"]


def test_nganh_khong_co_data_tra_rong_khong_bia():
    for slug in ["tivi", "laptop", "dien-thoai"]:
        r = f(nganh=slug)
        assert r["ten"] == "" and r["tong"] == 0 and r["san_pham"] == [], slug


def test_loc_hang_va_gia_chay_that():
    r = f(nganh="may-lanh", hang="Daikin", gia_max=15000000, sap_xep="gia_tang")
    assert r["tong"] > 0
    gia = [s["gia"] for s in r["san_pham"]]
    assert all(s["hang"] == "Daikin" for s in r["san_pham"])
    assert all(g <= 15000000 for g in gia)
    assert gia == sorted(gia)          # sap xep gia tang


def test_slug_khong_ton_tai_khong_no():
    r = f(nganh="khong-co-nganh-nay")
    assert r["san_pham"] == [] and r["tong"] == 0
