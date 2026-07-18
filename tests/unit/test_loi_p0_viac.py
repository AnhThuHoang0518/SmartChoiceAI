# -*- coding: utf-8 -*-
import pytest

from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.nganh.khung import nganh_theo_ten, tim_nganh
from backend.app.services.llm import LuatLLM


@pytest.fixture(autouse=True)
def _phien_sach():
    phien.don_het()
    chat_api._LLM = LuatLLM()
    yield
    phien.don_het()


def _chat(text: str):
    return chat_api.chat(chat_api.TinNhan(tin_nhan=text))


def test_tc117_tablet_co_cum_man_hinh_khong_duoc_router_sang_man_hinh():
    assert tim_nganh("tablet học online, màn hình lớn").ten == "may_tinh_bang"

    r = _chat("tablet học online, màn hình lớn, pin tốt, dưới 10 triệu")

    assert r.loai == "tu_van"
    assert r.thong_ke["nganh"] == "may_tinh_bang"
    assert any(
        n["truong"] == "pin_mah"
        for u in r.top3
        for n in u.get("nguon", [])
    )


@pytest.mark.parametrize(
    "text",
    [
        "tôi cần máy tiết kiệm điện",
        "tôi cần máy chạy êm cho phòng ngủ",
        "sản phẩm nào dưới 10 triệu",
    ],
)
def test_tc126_127_129_chua_ro_nganh_phai_hoi_san_pham_truoc(text):
    r = _chat(text)

    assert r.loai == "cau_hoi"
    assert "sản phẩm" in r.text.lower()
    assert "ngân sách" not in r.text.lower()
    assert "diện tích" not in r.text.lower()
    assert phien.lay(r.phien_id)["nganh"] is None


def test_tc128_khong_xep_hang_truc_tiep_hai_nganh_khac_muc_dich():
    r = _chat("so sánh máy lạnh và tủ lạnh nào tiết kiệm điện hơn")

    assert r.loai == "khac_nganh"
    assert r.top3 == []
    assert "không thể xếp hạng trực tiếp" in r.text.lower()
    assert "máy lạnh" in r.text.lower()
    assert "tủ lạnh" in r.text.lower()


def test_tc102_va_khong_dau_khong_bi_hieu_thanh_tam_nen_va():
    nganh = nganh_theo_ten("man_hinh")
    assert nganh is not None

    nc = nganh.trich("màn hình gắn arm VESA va bàn sâu hẹp")
    assert nc.lay("tam_nen") is None

    nc_co_ngu_canh = nganh.trich("màn hình tấm nền VA")
    assert nc_co_ngu_canh.lay("tam_nen") == "va"


def test_tc136_so_dien_thoai_khong_duoc_hieu_thanh_ngan_sach():
    r = _chat("số tôi là 0912345678, gọi cho tôi khi có hàng")

    assert r.loai == "bao_mat"
    assert "0912345678" not in r.text
    assert "không thể tự gọi" in r.text.lower()
    assert "ngan_sach_max" not in r.o_nhu_cau
    assert r.thong_ke["cham_llm"] == 0


def _phien_co_top3():
    ma = phien.tao_phien()
    p = phien.lay(ma)
    p["nganh"] = "may_giat"
    p["top3_truoc"] = [
        {"ten": "Máy Alpha A", "gia": 1_000_000, "nguon": []},
        {
            "ten": "Máy Bravo B",
            "gia": 2_000_000,
            "nguon": [{
                "truong": "bao_hanh_dc_nam",
                "gia_tri": "10",
                "nguon": "catalog:Bảo hành động cơ",
                "lay_luc": "2026-01-01T00:00:00Z",
                "ma_sp": "B",
                "suy_luan": False,
            }],
        },
    ]
    return ma, p


def test_tc027_con_thu_hai_thieu_bang_dieu_khien_khong_chay_lai_ranking():
    ma, p = _phien_co_top3()
    top_cu = p["top3_truoc"]

    r = chat_api.chat(chat_api.TinNhan(
        phien_id=ma,
        tin_nhan="con thứ hai có bảng điều khiển tiếng Việt không?",
    ))

    assert r.loai == "thieu_du_lieu"
    assert "Máy Bravo B" in r.text
    assert "chưa có trường bảng điều khiển" in r.text
    assert r.top3 == top_cu
    assert r.thong_ke["cham_llm"] == 0


def test_tc148_bao_hanh_con_thu_hai_doc_dung_nguon_khong_vao_policy():
    ma, _ = _phien_co_top3()

    r = chat_api.chat(chat_api.TinNhan(
        phien_id=ma,
        tin_nhan="con thứ hai có bảo hành gì?",
    ))

    assert r.loai == "tra_loi_san_pham"
    assert "Máy Bravo B" in r.text
    assert "10 năm" in r.text
    assert r.thong_ke["san_pham_thu"] == 2
    assert r.thong_ke["cham_llm"] == 0


def test_tc149_truong_khong_co_schema_phai_noi_thieu_du_lieu():
    ma, _ = _phien_co_top3()

    r = chat_api.chat(chat_api.TinNhan(
        phien_id=ma,
        tin_nhan="máy 1 có thông số bí mật X không?",
    ))

    assert r.loai == "thieu_du_lieu"
    assert "chưa có trường thông số được hỏi" in r.text
    assert r.thong_ke["cham_llm"] == 0
