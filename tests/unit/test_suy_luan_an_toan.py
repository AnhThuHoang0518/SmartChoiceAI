# -*- coding: utf-8 -*-
"""Suy luận chỉ tạo ứng viên ngành; khách phải xác nhận trước khi tư vấn."""
from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.core.chuan_hoa_tv import goi_y_may_lanh_tu_nhu_cau_lam_mat
from backend.app.services.llm import LuatLLM


def _bat_dau(text: str):
    phien.don_het()
    chat_api._LLM = LuatLLM()
    return chat_api.chat(chat_api.TinNhan(tin_nhan=text))


def test_nhu_cau_giam_nong_chi_goi_y_chua_tu_chon_nganh():
    r = _bat_dau("nóng quá jj nên mua ở đây ko")

    assert r.loai == "xac_nhan_nganh"
    assert r.thong_ke["cham_llm"] == 0
    assert r.thong_ke["suy_luan"] is True
    assert r.top3 == []
    assert r.o_nhu_cau == {}
    assert r.goi_y == ["Đúng, tìm máy lạnh", "Tôi cần sản phẩm khác"]

    p = phien.lay(r.phien_id)
    assert p["nganh"] is None
    assert p["nhu_cau"].model_dump(exclude_none=True) == {"uu_tien": []}
    assert p["xac_nhan_nganh"]["nganh"] == "may_lanh"


def test_xac_nhan_tran_moi_chot_may_lanh_va_hoi_dien_tich_khong_llm():
    truoc = _bat_dau("nóng quá nên mua gì cho mát")
    r = chat_api.chat(chat_api.TinNhan(
        phien_id=truoc.phien_id,
        tin_nhan="Đúng, tìm máy lạnh",
    ))

    assert r.loai == "cau_hoi"
    assert "m²" in r.text
    assert r.thong_ke["cham_llm"] == 0
    assert r.top3 == []

    p = phien.lay(r.phien_id)
    assert p["nganh"] == "may_lanh"
    assert p["xac_nhan_nganh"] is None


def test_xac_nhan_kem_dien_tich_duoc_doc_luon_khong_bat_noi_lai():
    truoc = _bat_dau("nóng quá nên mua gì cho mát")
    r = chat_api.chat(chat_api.TinNhan(
        phien_id=truoc.phien_id,
        tin_nhan="Đúng, phòng 18m2",
    ))

    assert r.loai == "cau_hoi"
    assert r.o_nhu_cau["dien_tich_m2"] == 18
    assert "bao nhiêu" in r.text
    assert "m²" not in r.text
    assert phien.lay(r.phien_id)["nganh"] == "may_lanh"


def test_tu_choi_goi_y_thi_xoa_ung_vien_va_hoi_lai_san_pham():
    truoc = _bat_dau("nóng quá nên mua gì cho mát")
    r = chat_api.chat(chat_api.TinNhan(
        phien_id=truoc.phien_id,
        tin_nhan="Tôi cần sản phẩm khác",
    ))

    assert r.loai == "cau_hoi"
    assert "sản phẩm gì" in r.text
    assert r.thong_ke["cham_llm"] == 0
    p = phien.lay(r.phien_id)
    assert p["nganh"] is None
    assert p["xac_nhan_nganh"] is None


def test_cac_cau_co_nong_nhung_khong_phai_nhu_cau_lam_mat_bi_loai():
    for text in (
        "máy nước nóng nào tốt",
        "tủ lạnh không lạnh, máy bị nóng",
        "điện thoại bị nóng nên sửa ở đâu",
        "nước nóng nên mua bình nào",
    ):
        assert goi_y_may_lanh_tu_nhu_cau_lam_mat(text) is False, text


def test_noi_ro_nganh_khac_thi_thang_ung_vien_suy_luan_cu():
    truoc = _bat_dau("nóng quá nên mua gì cho mát")
    r = chat_api.chat(chat_api.TinNhan(
        phien_id=truoc.phien_id,
        tin_nhan="Tôi muốn mua máy nước nóng",
    ))

    assert r.loai != "xac_nhan_nganh"
    p = phien.lay(r.phien_id)
    assert p["xac_nhan_nganh"] is None
    assert p["nganh"] == "may_nuoc_nong"


def test_noi_ro_may_lanh_ngay_tu_dau_khong_hoi_xac_nhan_thua():
    r = _bat_dau("nóng quá nên mua máy lạnh nào")
    assert r.loai != "xac_nhan_nganh"
    assert phien.lay(r.phien_id)["nganh"] == "may_lanh"
