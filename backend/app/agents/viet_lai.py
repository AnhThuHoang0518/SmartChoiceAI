# -*- coding: utf-8 -*-
"""Dien dat bang ket qua thanh loi tu van - cho cham LLM THU HAI va cuoi cung.

LLM o day KHONG duoc tra catalog, KHONG biet san pham nao khac ton tai, KHONG
tinh gi. No chi nhan bang da tinh xong va viet lai cho de nghe. Cat nguon nhu
vay thi no khong co gi de bia - va cai gi con lot thi hau kiem chan.

Vong lap: viet -> hau kiem -> lech thi bao loi CU THE va bat viet lai -> qua
so lan cho phep thi ve ban du phong (kho nhung moi so deu that).
"""
from __future__ import annotations

from backend.app.guardrails.hau_kiem import ban_du_phong, hau_kiem
from backend.app.ranking.xep_hang import cfg
from backend.app.schemas.ket_qua import BangKetQua
from backend.app.schemas.nhu_cau import ONhuCauMayLanh
from backend.app.services.llm import LLM

HE_THONG = """Bạn là nhân viên tư vấn điện máy người Việt, xưng "em", gọi khách là "mình", kết câu bằng "ạ".

LUẬT TUYỆT ĐỐI:
1. CHỈ dùng số liệu có trong BẢNG KẾT QUẢ bên dưới. Không có số nào khác được xuất hiện.
2. Không dùng từ quảng cáo: "tốt nhất thị trường", "siêu phẩm", "đỉnh cao", "cực kỳ".
3. Không khen đều tất cả. Mỗi máy PHẢI nêu rõ được gì và MẤT gì.
4. Thông số phải dịch ra nghĩa thực tế (26 dB -> nằm ngủ gần như không nghe tiếng).
5. Nếu bảng có mục "Không đề xuất", phải chủ động nói vì sao không đề xuất máy đó.
6. Viết ngắn, như người bán hàng nói chuyện, không gạch đầu dòng dài dòng.
7. TỐI ĐA 150 từ. Mỗi máy 1-2 câu. Dài hơn là bị cắt.

Trả lời thẳng, không chào hỏi dài."""


def _bang_thanh_chu(bang: BangKetQua, nhu_cau: ONhuCauMayLanh) -> str:
    """Serialize bang -> van ban. Day la TOAN BO the gioi ma LLM nhin thay."""
    d = [f"NHU CẦU KHÁCH: phòng {nhu_cau.dien_tich_m2:.0f}m²"]
    if nhu_cau.co_nang:
        d.append(f"có nắng chiếu (tải nhiệt tương đương {bang.dien_tich_hieu_dung_m2}m²)")
    if nhu_cau.ngan_sach_max:
        d.append(f"ngân sách tối đa {nhu_cau.ngan_sach_max/1_000_000:.0f} triệu")
    if nhu_cau.loai_phong:
        d.append("phòng ngủ" if nhu_cau.loai_phong.value == "ngu" else "phòng khách")
    if nhu_cau.uu_tien:
        d.append("ưu tiên: " + ", ".join(u.value for u in nhu_cau.uu_tien))

    ra = [", ".join(d), ""]
    ra.append(f"Đã lọc {bang.tong_truoc_loc} máy còn {bang.con_lai_sau_loc} máy phù hợp.")
    ra.append("")
    ra.append("TOP 3:")
    for i, u in enumerate(bang.top3, 1):
        ra.append(f"{i}. {u.ten} — giá {u.gia:,d}đ".replace(",", "."))
        for h in u.hon:
            ra.append(f"   HƠN về {h.truc}: {h.cua_minh} (đối thủ: {h.doi_thu})")
        for k in u.kem:
            ra.append(f"   KÉM về {k.truc}: {k.cua_minh} (đối thủ: {k.doi_thu})")
        if not u.hon and not u.kem:
            ra.append("   (ngang bằng các máy còn lại trên mọi tiêu chí khách quan tâm)")

    if bang.loai_noi_bat:
        ra += ["", f"KHÔNG ĐỀ XUẤT: {bang.loai_noi_bat.ten} — {bang.loai_noi_bat.chi_tiet}"]
    return "\n".join(ra)


def viet_lai(bang: BangKetQua, nhu_cau: ONhuCauMayLanh, llm: LLM) -> dict:
    """Tra {text, nguon_llm, so_lan_bi_chan, loi_da_chan, ms}."""
    c = cfg()["hau_kiem"]
    du_lieu = _bang_thanh_chu(bang, nhu_cau)
    nguoi_dung = du_lieu
    da_chan: list[str] = []
    tong_ms = 0

    for lan in range(c["so_lan_bat_viet_lai_toi_da"] + 1):
        try:
            text, ms = llm.sinh_do(HE_THONG, nguoi_dung)
        except Exception:
            # LLM chet giua chung (mang, het quota, server sap) -> khong duoc 500
            # voi khach. Roi ve ban du phong nhu the LLM tra rong.
            text, ms = "", 0
        tong_ms += ms
        if not text:
            break                                   # LuatLLM / LLM hong -> ban du phong

        loi = hau_kiem(text, bang, nhu_cau, c["dung_sai_tuong_doi"])
        if not loi:
            return {
                "text": text,
                "nguon_llm": llm.ten,
                "so_lan_bi_chan": lan,
                "loi_da_chan": da_chan,
                "ms": tong_ms,
            }

        da_chan += loi
        # Bao loi CU THE chu khong phai "sai roi viet lai" - noi ro so nao sai
        # thi lan sau no bo dung so do, khong thi no sua lung tung cho khac.
        nguoi_dung = (
            f"{du_lieu}\n\n---\nBản nháp trước của bạn bị CHẶN vì bịa số liệu:\n"
            + "\n".join(f"- {x}" for x in loi)
            + "\n\nViết lại. Chỉ dùng số có trong bảng trên. Bỏ hẳn các số bị chặn."
        )

    return {
        "text": ban_du_phong(bang, cfg()["ban_du_phong"]["mau"]),
        "nguon_llm": "ban_du_phong",
        "so_lan_bi_chan": c["so_lan_bat_viet_lai_toi_da"] + 1,
        "loi_da_chan": da_chan,
        "ms": tong_ms,
    }
