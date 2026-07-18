# -*- coding: utf-8 -*-
import pytest

from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.core.chuan_hoa_tv import mau_thuan_tam_gia
from backend.app.core.giai_thich_kien_thuc import giai_thich_kien_thuc
from backend.app.nganh.khung import nganh_theo_ten
from backend.app.services.llm import LuatLLM


@pytest.fixture(autouse=True)
def _phien_sach():
    phien.don_het()
    chat_api._LLM = LuatLLM()
    yield
    phien.don_het()


def _chat(text: str, phien_id: str | None = None):
    return chat_api.chat(chat_api.TinNhan(tin_nhan=text, phien_id=phien_id))


def test_giai_thich_hp_khong_tu_dat_nguong_dien_tich():
    text = giai_thich_kien_thuc("HP là gì?")

    assert text is not None
    assert "hãng công bố" in text.lower()
    assert "15m²" not in text
    assert "20m²" not in text
    assert "30m²" not in text


def test_giai_thich_inverter_khong_bao_dam_em_va_it_ton_dien():
    text = giai_thich_kien_thuc("Inverter khác gì non-Inverter?")

    assert text is not None
    assert "chưa đủ để kết luận" in text.lower()
    assert "cùng điều kiện" in text.lower()
    assert "nên êm hơn và tốn ít điện hơn" not in text.lower()


def test_tiet_kiem_dien_khong_bi_hieu_thanh_gia_re():
    assert not mau_thuan_tam_gia(
        "Tôi muốn máy lạnh cao cấp nhất và tiết kiệm điện nhất"
    )
    assert mau_thuan_tam_gia(
        "Tôi muốn máy lạnh cao cấp nhất nhưng giá rẻ nhất"
    )


def test_hoi_gia_hang_chua_co_nganh_khong_mac_dinh_may_lanh():
    hang = chat_api.catalog()[0].hang

    r = _chat(f"{hang} giá bao nhiêu?")

    assert r.loai == "cau_hoi"
    assert "loại sản phẩm nào" in r.text.lower()
    assert "không mặc định sang máy lạnh" in r.text.lower()
    assert r.thong_ke["cham_llm"] == 0
    assert phien.lay(r.phien_id)["hang_dang_hoi_gia"] == hang


def test_hoi_gia_hang_nho_hang_sau_khi_khach_chon_nganh():
    hang = chat_api.catalog()[0].hang
    r1 = _chat(f"{hang} giá bao nhiêu?")

    r2 = _chat("Máy lạnh", r1.phien_id)

    assert r2.loai == "giai_thich"
    assert f"hãng {hang}" in r2.text
    assert "giá từ" in r2.text.lower()
    assert r2.thong_ke["cham_llm"] == 0
    assert "hang_dang_hoi_gia" not in phien.lay(r1.phien_id)


@pytest.mark.parametrize(
    ("query", "nganh", "truong"),
    [
        ("Micro nào dùng được với iPhone?", "micro", "tuong_thich_thiet_bi"),
        ("Đồng hồ nào gọi độc lập bằng eSIM?", "dong_ho", "gps_sim_doc_lap"),
        ("PC nào nâng RAM và SSD được?", "may_tinh_ban", "kha_nang_nang_cap"),
        ("Màn hình nào 144 Hz?", "man_hinh", "tan_so_quet"),
        ("Máy in nào tốn ít tiền mực nhất?", "may_in", "chi_phi_muc"),
        ("Tablet nào hỗ trợ bút và độ trễ thấp?", "may_tinh_bang", "but_do_tre"),
        ("Tablet nào chơi game mượt?", "may_tinh_bang", "hieu_nang_game"),
    ],
)
def test_dien_tu_thieu_field_phai_dung_truoc_xep_hang(query, nganh, truong):
    r = _chat(query)

    assert r.loai == "thieu_du_lieu"
    assert r.top3 == []
    assert r.thong_ke["nganh"] == nganh
    assert r.thong_ke["truong_thieu"] == truong
    assert r.thong_ke["cham_llm"] == 0


def test_may_in_doc_dung_hang_nghin_trang_moi_thang():
    nganh = nganh_theo_ten("may_in")

    nc = nganh.trich("Máy in văn phòng 2.000 trang/tháng")

    assert nc.lay("cong_suat_thang_min") == 2000


def test_may_in_wifi_co_gach_noi_van_la_hard_filter():
    r = _chat("Máy in qua Wi-Fi dưới 10 triệu")

    assert r.loai == "tu_van"
    assert r.top3
    assert all(
        "wifi" in str(u.get("chu", {}).get("ket_noi", "")).lower()
        or any(
            n.get("truong") == "ket_noi" and "wifi" in str(n.get("gia_tri", "")).lower()
            for n in u.get("nguon", [])
        )
        for u in r.top3
    )


def test_micro_hat_hay_nhat_khong_xep_hang_theo_gia():
    r = _chat("Top 3 micro hát hay nhất")

    assert r.loai == "chu_quan"
    assert r.top3 == []
    assert r.thong_ke["cham_llm"] == 0


def test_chup_anh_dep_nhat_de_guard_camera_xu_ly_khong_phai_gu_tham_my():
    r = _chat("Tablet nào chụp ảnh đẹp nhất?")

    assert r.loai == "thieu_du_lieu"
    assert r.thong_ke["truong_thieu"] == "camera_dinh_luong"
    assert r.thong_ke["cham_llm"] == 0
