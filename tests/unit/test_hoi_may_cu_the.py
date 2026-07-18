# -*- coding: utf-8 -*-
"""Khach nhac MA may cu the ('LG 179380', tu landing) -> tu van thang ve may
do, KHONG hieu nham ma so thanh ngan sach (bug tu landing card)."""
import os
os.environ.setdefault("LLM_NHA_CUNG_CAP", "luat")

from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.services.llm import LuatLLM


def _chat(text: str):
    phien.don_het(); chat_api._LLM = LuatLLM()
    return chat_api.chat(chat_api.TinNhan(tin_nhan=text))


def test_ma_may_khong_bi_hieu_nham_thanh_ngan_sach():
    r = _chat("Tư vấn máy lạnh LG 179380, có hợp phòng mình không?")
    assert r.loai == "giai_thich"
    assert r.o_nhu_cau.get("ngan_sach_max") is None      # 179380 KHONG thanh tien
    assert "179380" in r.text


def test_go_thang_ma_may_van_nhan_ra():
    r = _chat("LG 179380 thế nào?")
    assert r.loai == "giai_thich" and "máy lạnh" in r.text.lower()


def test_cau_thuong_khong_bi_anh_huong():
    r = _chat("máy lạnh 15 triệu phòng 18m2 không nắng phòng ngủ")
    assert r.loai == "tu_van"
