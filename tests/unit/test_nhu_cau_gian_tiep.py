# -*- coding: utf-8 -*-
"""Khach noi TINH HUONG thay vi ten san pham -> hieu dung nhu cau gian tiep.

'toc uot' -> may say TOC (khong co data -> tu choi that, KHONG day sang may
say quan ao). 'nha nong' -> may lanh. Chong ca lop 'chao chung chung khi
khach da noi ro van de'.
"""
from backend.app.core.nhu_cau_gian_tiep import nhu_cau_gian_tiep
from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.services.llm import LuatLLM


def _chat_moi(text: str):
    phien.don_het()
    chat_api._LLM = LuatLLM()
    return chat_api.chat(chat_api.TinNhan(tin_nhan=text))


def test_tinh_huong_ngoai_data_tu_choi_that():
    for cau, sp in [("tóc tôi bị ướt cần mua gì", "máy sấy tóc"),
                    ("muốn nghe nhạc to", "loa"),
                    ("nấu cơm", "nồi cơm điện")]:
        r = nhu_cau_gian_tiep(cau)
        assert r and r[0] == "ngoai", cau
    # QUAN TRONG: 'toc uot' KHONG duoc day sang may say quan ao
    r = nhu_cau_gian_tiep("tóc bị ướt")
    assert r[1] == "máy sấy tóc"


def test_tinh_huong_co_data_anh_xa_dung_nganh():
    for cau, nganh in [("nhà nóng quá", "máy lạnh"),
                       ("quần áo lâu khô mùa mưa", "máy sấy"),
                       ("đồ ăn hay bị hỏng", "tủ lạnh"),
                       ("tắm nước lạnh run quá", "máy nước nóng"),
                       ("rửa bát nhiều mệt lắm", "máy rửa chén"),
                       ("trữ đông nhiều thịt cá", "tủ đông")]:
        r = nhu_cau_gian_tiep(cau)
        assert r and r[0] == "nganh" and r[1] == nganh, cau


def test_cau_ro_rang_khong_kich_hoat():
    # da goi ten san pham thi khong can suy gian tiep
    assert nhu_cau_gian_tiep("máy lạnh 15 triệu") is None
    assert nhu_cau_gian_tiep("mua tủ lạnh") is None


def test_router_chi_goi_y_nganh_chua_tu_loc_san_pham():
    r = _chat_moi("quần áo lâu khô mùa mưa")

    assert r.loai == "xac_nhan_nganh"
    assert r.thong_ke["suy_luan"] is True
    assert r.thong_ke["cham_llm"] == 0
    assert r.top3 == []
    p = phien.lay(r.phien_id)
    assert p["nganh"] is None
    assert p["xac_nhan_nganh_gian_tiep"]["san_pham"] == "máy sấy"


def test_xac_nhan_nganh_gian_tiep_moi_chay_flow_va_giu_nhu_cau_moi():
    truoc = _chat_moi("quần áo lâu khô mùa mưa")
    r = chat_api.chat(chat_api.TinNhan(
        phien_id=truoc.phien_id,
        tin_nhan="Đúng, tải trọng 9 kg dưới 20 triệu",
    ))

    assert r.loai != "xac_nhan_nganh"
    p = phien.lay(r.phien_id)
    assert p["nganh"] == "may_say"
    assert "xac_nhan_nganh_gian_tiep" not in p


def test_tu_choi_goi_y_gian_tiep_khong_chot_nganh():
    truoc = _chat_moi("đồ ăn hay bị hỏng")
    r = chat_api.chat(chat_api.TinNhan(
        phien_id=truoc.phien_id,
        tin_nhan="Tôi cần sản phẩm khác",
    ))

    assert r.loai == "cau_hoi"
    assert phien.lay(r.phien_id)["nganh"] is None
    assert "xac_nhan_nganh_gian_tiep" not in phien.lay(r.phien_id)


def test_router_toc_uot_tu_choi_that_khong_nham_may_say_quan_ao():
    r = _chat_moi("tóc bị ướt cần mua gì")

    assert r.loai == "ngoai_pham_vi"
    assert "máy sấy tóc" in r.text.lower()
    assert r.top3 == []


def test_cau_vua_giong_hoi_chung_vua_suy_duoc_thi_uu_tien_suy_luan():
    # "tóc khô lâu THÌ NÊN CHỌN SẢN PHẨM NÀO" vua giong cau hoi chung (can_hoi
    # lam ro nganh) vua suy duoc may say toc -> phai suy luan, KHONG hoi chung.
    r = _chat_moi("tóc tôi khô lâu thì nên chọn sản phẩm nào")
    assert r.loai == "ngoai_pham_vi"
    assert "máy sấy tóc" in r.text.lower()

    r2 = _chat_moi("đồ ăn hay hỏng nên chọn sản phẩm nào")
    assert r2.loai == "xac_nhan_nganh"
    assert phien.lay(r2.phien_id)["xac_nhan_nganh_gian_tiep"]["san_pham"] == "tủ lạnh"


def test_cau_that_su_chung_chung_van_hoi_lai():
    # khong suy duoc tinh huong -> van hoi lam ro (khong bia nganh)
    r = _chat_moi("tôi muốn mua gì đó")
    assert r.loai == "cau_hoi"
    assert phien.lay(r.phien_id)["nganh"] is None


def test_noi_ro_micro_thu_am_khong_bi_xem_la_suy_luan_gian_tiep():
    r = _chat_moi("micro thu âm: Tôi quay video 6 giờ, pin có đủ không?")

    assert r.loai != "xac_nhan_nganh"
    assert phien.lay(r.phien_id)["nganh"] == "micro"
