# -*- coding: utf-8 -*-
"""LLM DE XUAT UNG VIEN nganh - lop vot khi regex + embedding tit.

AN TOAN: LLM chi chon 1 ten trong danh sach dong 13 nganh, hoac 'khong_ro'.
Ten ngoai danh sach -> loai. Van bat khach xac nhan (khong tu chot). Khong khoa
/ LuatLLM -> None -> hoi chung nhu cu.
"""
from backend.app.agents.suy_luan_nganh_llm import de_xuat_nganh_llm
from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.services.llm import LLM, LuatLLM


class _LLMTra(LLM):
    ten = "gia"

    def __init__(self, noi_dung):
        self._nd = noi_dung

    def sinh(self, he_thong, nguoi_dung, json_mode=False):
        return self._nd


def test_llm_chon_nganh_trong_danh_sach_thi_nhan():
    assert de_xuat_nganh_llm("x", _LLMTra('{"nganh": "màn hình máy tính"}')) == "màn hình máy tính"
    assert de_xuat_nganh_llm("x", _LLMTra('{"nganh": "máy giặt"}')) == "máy giặt"


def test_llm_chon_ten_ngoai_danh_sach_thi_loai():
    assert de_xuat_nganh_llm("x", _LLMTra('{"nganh": "xe máy điện"}')) is None
    assert de_xuat_nganh_llm("x", _LLMTra('{"nganh": "khong_ro"}')) is None
    assert de_xuat_nganh_llm("x", _LLMTra("")) is None
    assert de_xuat_nganh_llm("x", _LLMTra("không phải json")) is None


def test_luat_llm_khong_de_xuat_gi():
    assert de_xuat_nganh_llm("cho con học online", LuatLLM()) is None


def _chat(text, llm, phien_id=None):
    if phien_id is None:
        phien.don_het()
    chat_api._LLM = llm
    return chat_api.chat(chat_api.TinNhan(tin_nhan=text, phien_id=phien_id))


def test_router_dung_llm_de_xuat_khi_regex_tit_va_bat_xac_nhan():
    cau = "tôi cần thiết bị trình chiếu tài liệu lớn nên sắm gì"
    r = _chat(cau, _LLMTra('{"nganh": "màn hình máy tính"}'))
    assert r.loai == "xac_nhan_nganh"
    assert r.thong_ke["bang_chung"] == "suy_nganh_ai"
    assert r.thong_ke["nganh_goi_y"] == "màn hình máy tính"
    # xac nhan -> vao dung nganh that
    r2 = _chat("Đúng", _LLMTra('{"nganh": "màn hình máy tính"}'), phien_id=r.phien_id)
    assert phien.lay(r.phien_id)["nganh"] == "man_hinh"


def test_router_khong_khoa_van_hoi_chung_khong_doi_hanh_vi():
    cau = "tôi cần thiết bị trình chiếu tài liệu lớn nên sắm gì"
    r = _chat(cau, LuatLLM())
    assert r.loai == "cau_hoi"
    assert phien.lay(r.phien_id)["nganh"] is None


def test_router_llm_bia_ten_khong_bi_chot_nganh():
    cau = "tôi cần thiết bị trình chiếu tài liệu lớn nên sắm gì"
    r = _chat(cau, _LLMTra('{"nganh": "máy bay"}'))
    assert r.loai == "cau_hoi"          # ten bia bi loai -> hoi chung
    assert phien.lay(r.phien_id)["nganh"] is None
