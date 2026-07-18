# -*- coding: utf-8 -*-
"""Thu tu hoi: NGAN SACH truoc, roi he TU DO gia tri thong tin hoi o dang gia
(loai/hieu suat) - KHONG ep kg/so nguoi. Khach da cho spec thi tra ket qua ngay,
khong cat ngang.

Wan (chu SP): 'mn thuong ko hoi kg' -> gia truoc, kg/so nguoi ha xuong tuy chon.
"""
from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.services.llm import LuatLLM


def _flow(msgs):
    phien.don_het()
    chat_api._LLM = LuatLLM()
    pid = None
    outs = []
    for m in msgs:
        r = chat_api.chat(chat_api.TinNhan(phien_id=pid, tin_nhan=m))
        pid = r.phien_id
        outs.append(r)
    return outs, pid


def test_may_say_hoi_gia_truoc_khong_hoi_kg():
    (r_nganh, r_gia, r_loai), pid = _flow(["máy sấy", "10 triệu", "bơm nhiệt"])
    # cau hoi dau tien sau khi chon nganh la NGAN SACH, khong phai kg
    assert r_nganh.loai == "cau_hoi"
    assert "bao nhiêu" in r_nganh.text.lower() and "kg" not in r_nganh.text.lower()
    # sau ngan sach: he tu do -> hoi LOAI (hieu suat), khong hoi kg
    assert r_gia.loai == "cau_hoi" and r_gia.thong_ke.get("hoi_them")
    assert "kg" not in r_gia.text.lower()
    # tra loi loai xong -> ra tu van
    assert r_loai.loai == "tu_van" and r_loai.top3


def test_khach_cho_kg_va_gia_thi_tra_ngay_khong_cat_ngang():
    (r,), _ = _flow(["máy sấy 9kg dưới 20 triệu"])
    assert r.loai == "tu_van" and r.top3


def test_may_giat_cho_so_nguoi_va_gia_tra_ngay():
    (r,), _ = _flow(["máy giặt nhà 4 người dưới 12 triệu"])
    assert r.loai == "tu_van" and r.top3


def test_khong_hoi_them_lan_hai_neu_khach_bo_qua():
    # may say: sau ngan sach hoi LOAI 1 lan; khach lo di -> KHONG hoi loai mai
    outs, pid = _flow(["máy sấy", "10 triệu"])
    assert outs[-1].loai == "cau_hoi" and outs[-1].thong_ke.get("hoi_them")
    r2 = chat_api.chat(chat_api.TinNhan(phien_id=pid, tin_nhan="máy nào cũng được"))
    assert r2.loai in ("tu_van", "khong_co_may")   # khong ket vao hoi loai mai
