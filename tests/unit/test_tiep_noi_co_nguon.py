# -*- coding: utf-8 -*-
from pathlib import Path

from backend.app.api import chat as chat_api
from backend.app.core import phien
from backend.app.core.hoi_tiep_noi import (
    canh_bao_may_lanh_chua_co_nguon,
    giai_thich_truong,
    tieu_chi_may_lanh_chua_co_nguon,
    tra_loi_tiet_kiem_dien,
)
from backend.app.services.llm import LuatLLM

# Tat ca ten/so ben duoi la du lieu gia lap, khong chep catalog that.


def _sp(ten: str, truong: str, gia_tri: str | None) -> dict:
    return {
        "ten": ten,
        "gia": 1_000_000,
        "diem": 0.5,
        "hon": [],
        "kem": [],
        "nguon": [{"truong": truong, "gia_tri": gia_tri}],
    }


def test_tu_nao_it_ton_dien_tra_thang_tu_nguon_khong_llm():
    top = [
        _sp("Tủ Alpha mẫu A", "dien_kwh_ngay", "2.4"),
        _sp("Tủ Bravo mẫu B", "dien_kwh_ngay", "1.2"),
    ]
    ket = tra_loi_tiet_kiem_dien(
        "Tủ nào ít tốn điện? Tủ nào ít tốn điện?", top, "tu_dong_mat"
    )

    assert ket is not None
    text, truong = ket
    assert truong == "dien_kwh_ngay"
    assert "Tủ Bravo mẫu B" in text
    assert "1,2 kWh/ngày" in text
    assert "Tủ Alpha mẫu A: 2,4 kWh/ngày" in text


def test_thieu_dien_nang_mot_may_thi_khong_tuyen_bo_may_thang():
    top = [
        _sp("Máy có số", "dien_kwh_ngay", "1.15"),
        _sp("Máy thiếu số", "dien_kwh_ngay", None),
    ]
    text, _ = tra_loi_tiet_kiem_dien(
        "tủ nào tiết kiệm điện nhất", top, "tu_dong_mat"
    )
    assert "chưa thể chốt" in text
    assert "Máy thiếu số" in text
    assert "thấp nhất" not in text


def test_api_cau_hoi_dien_nang_dung_top_truoc_va_cham_llm_0():
    phien.don_het()
    chat_api._LLM = LuatLLM()
    ma = phien.tao_phien()
    p = phien.lay(ma)
    p["nganh"] = "tu_dong_mat"
    p["top3_truoc"] = [
        _sp("Tủ Alpha mẫu A", "dien_kwh_ngay", "2.4"),
        _sp("Tủ Bravo mẫu B", "dien_kwh_ngay", "1.2"),
    ]

    r = chat_api.chat(chat_api.TinNhan(
        phien_id=ma, tin_nhan="Tủ nào ít tốn điện?"
    ))
    assert r.loai == "tra_loi_truong"
    assert r.thong_ke["cham_llm"] == 0
    assert r.thong_ke["truong_doi_chieu"] == "dien_kwh_ngay"
    assert "1,2 kWh/ngày" in r.text


def test_sau_la_gi_duoc_giai_thich_khong_lap_cau_tu_van_cu():
    phien.don_het()
    chat_api._LLM = LuatLLM()
    r = chat_api.chat(chat_api.TinNhan(tin_nhan="sâu là cái gì"))
    assert r.loai == "giai_thich_truong"
    assert r.thong_ke["cham_llm"] == 0
    assert "mặt trước đến mặt sau" in r.text
    assert giai_thich_truong("sâu là cái gì") == r.text


def test_pc_can_card_roi_bi_chan_truoc_xep_hang():
    phien.don_het()
    chat_api._LLM = LuatLLM()
    r = chat_api.chat(chat_api.TinNhan(
        tin_nhan="PC cần card rời, ngân sách 25 triệu"
    ))

    assert r.loai == "thieu_du_lieu"
    assert r.top3 == []
    assert r.thong_ke["cham_llm"] == 0
    assert r.thong_ke["truong_thieu"] == "gpu_roi"
    assert "chưa có trường card đồ họa/GPU" in r.text
    assert "không đề xuất bừa" in r.text
    assert r.o_nhu_cau["ngan_sach_max"] == 25_000_000


def test_tre_nho_va_nhiet_do_chi_tao_canh_bao_thieu_nguon():
    tieu_chi = tieu_chi_may_lanh_chua_co_nguon(
        "máy lạnh phòng trẻ nhỏ, nhiệt độ cài đặt thế nào"
    )
    assert tieu_chi == {"tre_nho", "nhiet_do"}
    text = canh_bao_may_lanh_chua_co_nguon(tieu_chi)
    assert "chế độ riêng cho trẻ nhỏ" in text
    assert "dải nhiệt độ cài đặt" in text
    assert "chỉ dựa trên những thông số có nguồn" in text


def test_api_tu_van_may_lanh_phai_noi_ro_tieu_chi_chua_co_nguon():
    phien.don_het()
    chat_api._LLM = LuatLLM()
    r = chat_api.chat(chat_api.TinNhan(
        tin_nhan=("máy lạnh 30tr cho phòng trẻ nhỏ 12m2 không nắng, "
                  "nhiệt độ cài đặt thế nào")
    ))

    assert r.loai == "tu_van"
    assert "catalog hiện chưa có trường" in r.text
    assert "chế độ riêng cho trẻ nhỏ" in r.text
    assert "dải nhiệt độ cài đặt" in r.text
    assert "chỉ dựa trên những thông số có nguồn" in r.text


def test_tts_chi_bo_ma_model_khi_doc_khong_doi_giao_dien():
    html = Path("frontend/chat/index.html").read_text(encoding="utf-8")
    assert "function boMaTrongTenSanPhamKhiDoc(text, sanPham)" in html
    assert "filter(t => !/\\d/.test(t))" in html
    assert "docTo(d.text, sanPhamDoc)" in html
    assert "sanPhamDoc.push(d.loai_noi_bat)" in html
    # Ten hien tren card van dung nguyen u.ten, khong qua ham bo ma.
    assert "(i+1) + '. ' + u.ten" in html
