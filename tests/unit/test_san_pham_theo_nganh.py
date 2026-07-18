# -*- coding: utf-8 -*-
"""Endpoint /api/san-pham cho trang danh muc landing: san pham THAT tu catalog,
KHONG mock. Nganh co data -> tra san pham + danh sach hang; nganh khong co data
-> rong (UI hien 'dang cap nhat'). Loc hang/gia + sap xep chay tren data that."""
from backend.app.api.chat import san_pham_theo_nganh as f
from backend.app.api.chat import danh_muc_landing, khuyen_mai_that


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


def test_khuyen_mai_landing_pho_thong_da_hang():
    km = khuyen_mai_that()
    assert 1 <= len(km) <= 4
    for d in km:
        assert d["gia"] <= 20_000_000, d["ten"]        # tam pho thong
        assert d["gia"] < d["gia_goc"] and d["phan_tram"] > 0
    hang = [d["ten"].split()[0] for d in km]
    assert len(set(hang)) == len(hang)                 # moi hang 1 may (da dang)


def test_danh_muc_landing_moi_muc_co_anh_that_khop_nganh():
    from backend.app.api.chat import _catalog_theo_slug, _anh_sp
    dm = danh_muc_landing()
    assert len(dm) >= 8
    anh = _anh_sp()
    for d in dm:
        # moi danh muc co san pham that + anh dai dien la anh THAT (khong lech nhan)
        assert d["tong"] > 0, d["ten"]
        assert d["anh_url"].startswith("http"), d["ten"]
        # anh dai dien phai thuoc DUNG nganh do (map tu ma_sp cua san pham nganh)
        _, ds = _catalog_theo_slug(d["slug"])
        anh_nganh = {anh.get(str(s.ma_sp), "") for s in ds}
        assert d["anh_url"] in anh_nganh, d["ten"]
