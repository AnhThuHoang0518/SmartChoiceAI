# -*- coding: utf-8 -*-
"""Khach noi TINH HUONG thay vi ten san pham -> hieu dung nhu cau gian tiep.

'toc uot' -> may say TOC (khong co data -> tu choi that, KHONG day sang may
say quan ao). 'nha nong' -> may lanh. Chong ca lop 'chao chung chung khi
khach da noi ro van de'.
"""
from backend.app.core.nhu_cau_gian_tiep import nhu_cau_gian_tiep


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
