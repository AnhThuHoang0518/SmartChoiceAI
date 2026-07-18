# -*- coding: utf-8 -*-
"""Chan LOP LOI 'va cham tu khoa': san pham khac dinh tu khoa nganh nhung
KHONG co du lieu -> tuyet doi khong dinh tuyen sai nganh (bug 'may say toc'
-> may say quan ao, 'tu dong'='tu dong' automatic -> tu dong/tu mat).

Moi khi phat hien va cham moi tren demo: them 1 dong tu_khoa_loai_tru trong
config (khung) hoac NGANH_KHAC (chuan_hoa_tv) + 1 dong o day.
"""
import os

os.environ.setdefault("LLM_NHA_CUNG_CAP", "luat")

from backend.app.nganh.khung import tim_nganh  # noqa: E402
from backend.app.core.chuan_hoa_tv import (  # noqa: E402
    co_nganh_may_lanh,
    co_nganh_tu_lanh,
    nganh_ngoai_pham_vi,
)


def _nganh_khung(cau: str) -> str | None:
    ng = tim_nganh(cau)
    return ng.ten if ng else None


def test_may_say_toc_khong_phai_may_say_quan_ao():
    assert _nganh_khung("máy sấy tóc") != "may_say"
    assert _nganh_khung("máy sấy tay giá rẻ") != "may_say"
    # nhung may say quan ao THAT van nhan dung
    assert _nganh_khung("máy sấy quần áo nhà 4 người") == "may_say"


def test_tu_dong_automatic_khong_phai_tu_dong_mat():
    for cau in ["máy pha cà phê tự động", "cửa tự động", "máy giặt tự động",
                "chế độ tự động", "tưới cây tự động"]:
        assert _nganh_khung(cau) != "tu_dong_mat", cau
    # tu dong/tu mat THAT (tru thuc pham) van nhan dung
    assert _nganh_khung("tủ đông trữ đông thực phẩm") == "tu_dong_mat"


def test_micro_usb_sd_khong_phai_micro_am_thanh():
    for cau in ["cáp micro usb", "thẻ nhớ micro sd", "cổng micro"]:
        assert _nganh_khung(cau) != "micro", cau
    assert _nganh_khung("micro thu âm 1 triệu") == "micro"


def test_dong_ho_treo_tuong_khong_phai_smartwatch():
    for cau in ["đồng hồ treo tường", "đồng hồ cơ", "đồng hồ nước"]:
        assert _nganh_khung(cau) != "dong_ho", cau
    assert _nganh_khung("đồng hồ thông minh 3 triệu") == "dong_ho"


def test_man_hinh_dien_thoai_khong_phai_man_hinh_may_tinh():
    assert _nganh_khung("màn hình điện thoại iphone") != "man_hinh"
    assert _nganh_khung("màn hình máy tính 27 inch") == "man_hinh"


def test_quat_dieu_hoa_khong_phai_may_lanh():
    assert co_nganh_may_lanh("quạt điều hòa cho phòng khách") is False
    assert nganh_ngoai_pham_vi("quạt điều hòa cho phòng khách") is not None
    # may lanh THAT van trong pham vi
    assert co_nganh_may_lanh("máy lạnh 1.5HP") is True
    assert nganh_ngoai_pham_vi("máy lạnh và tivi") is None


def test_may_loc_va_may_say_toc_bao_ngoai_pham_vi():
    assert nganh_ngoai_pham_vi("máy lọc nước nóng lạnh") is not None
    assert nganh_ngoai_pham_vi("máy sấy tóc") is not None
