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

_LUAT_CHUNG = """Bạn là nhân viên tư vấn điện máy người Việt, xưng "em", gọi khách là "mình", kết câu bằng "ạ".

LUẬT TUYỆT ĐỐI:
1. CHỈ dùng số liệu có trong BẢNG KẾT QUẢ bên dưới. Không có số nào khác được xuất hiện.
2. Không dùng từ quảng cáo: "tốt nhất thị trường", "siêu phẩm", "đỉnh cao", "cực kỳ".
3. Không khen đều tất cả. Mỗi máy PHẢI nêu rõ được gì và MẤT gì.
4. Nếu bảng có mục "Không đề xuất", phải chủ động nói vì sao không đề xuất máy đó.
5. TỐI ĐA 150 từ. Dài hơn là bị cắt.

Trả lời thẳng, không chào hỏi dài."""

# Giong BINH DAN (mac dinh): khach khong hieu thong so - dich het ra doi thuong.
HE_THONG = _LUAT_CHUNG + """
GIỌNG: khách KHÔNG rành kỹ thuật. Thông số phải dịch ra nghĩa thực tế
(26 dB -> nằm ngủ gần như không nghe tiếng; CSPF cao hơn -> tiền điện tháng thấp hơn).
Nói như người bán hàng thân thiện, tập trung "máy này hơn máy kia chỗ nào" chứ không liệt kê số."""

# Giong KY THUAT: khach ranh thong so (tu nhan biet qua ngon ngu ho go).
HE_THONG_KY_THUAT = _LUAT_CHUNG + """
GIỌNG: khách AM HIỂU kỹ thuật. Nói thẳng thông số kèm đơn vị (dB, CSPF, sao năng lượng,
dải m², giá gốc/giá khuyến mãi), so sánh trực tiếp bằng số, không cần ví von đời thường.
Vẫn giữ trade-off rõ ràng."""


def _bang_thanh_chu(
    bang: BangKetQua, nhu_cau: ONhuCauMayLanh, giong: str = "binh_dan"
) -> str:
    """Serialize bang -> van ban. Day la TOAN BO the gioi ma LLM nhin thay.

    Giong ky_thuat -> kem dong thong so day du tung may (khach ranh so duoc
    xem het; cac truong nay deu co nguon nen hau kiem cho noi).
    """
    d = [f"NHU CẦU KHÁCH: phòng {nhu_cau.dien_tich_m2:.0f}m²"]
    if nhu_cau.co_nang:
        d.append(f"có nắng chiếu (tải nhiệt tương đương {bang.dien_tich_hieu_dung_m2}m²)")
    if nhu_cau.ngan_sach_max and nhu_cau.ngan_sach_max >= 10**11:
        d.append("KHÔNG giới hạn ngân sách (khách đã xác nhận)")
    elif nhu_cau.ngan_sach_max:
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
        if giong == "ky_thuat":
            th = {n.truong: n.gia_tri for n in u.nguon}
            chi_tiet = []
            if th.get("pham_vi"):
                chi_tiet.append(f"dải {th['pham_vi']}")
            if th.get("do_on_db") not in (None, "None"):
                chi_tiet.append(f"độ ồn {th['do_on_db']} dB")
            if th.get("cspf") not in (None, "None"):
                chi_tiet.append(f"CSPF {th['cspf']}")
            if th.get("sao") not in (None, "None"):
                chi_tiet.append(f"{th['sao']} sao")
            if th.get("gia_goc") and str(th["gia_goc"]) != str(u.gia):
                chi_tiet.append(f"giá gốc {int(float(th['gia_goc'])):,d}đ".replace(",", "."))
            if chi_tiet:
                ra.append("   Thông số: " + " · ".join(chi_tiet))

    if bang.loai_noi_bat:
        ra += ["", f"KHÔNG ĐỀ XUẤT: {bang.loai_noi_bat.ten} — {bang.loai_noi_bat.chi_tiet}"]
    return "\n".join(ra)


def viet_lai(
    bang: BangKetQua,
    nhu_cau,
    llm: LLM,
    giong: str = "binh_dan",
    mo_ta_nhu_cau: str | None = None,
) -> dict:
    """Tra {text, nguon_llm, so_lan_bi_chan, loi_da_chan, ms}.

    mo_ta_nhu_cau: nganh khac (tu lanh...) tu xay chuoi mo ta nhu cau + bang
    ket qua roi dua vao day - vong hau kiem/viet lai dung chung, chi phan
    serialize la rieng tung nganh.
    """
    c = cfg()["hau_kiem"]
    he_thong = HE_THONG_KY_THUAT if giong == "ky_thuat" else HE_THONG
    du_lieu = mo_ta_nhu_cau if mo_ta_nhu_cau is not None else _bang_thanh_chu(bang, nhu_cau, giong)
    nguoi_dung = du_lieu
    da_chan: list[str] = []
    tong_ms = 0

    for lan in range(c["so_lan_bat_viet_lai_toi_da"] + 1):
        try:
            text, ms = llm.sinh_do(he_thong, nguoi_dung)
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

    # Nganh khac (di qua mo_ta_nhu_cau) khong duoc muon template may lanh -
    # "tai nhiet ?m²" voi tu lanh la vo nghia. Dung mau chung chi liet ke ten+gia.
    mau_du_phong = (
        cfg()["ban_du_phong"]["mau"] if mo_ta_nhu_cau is None
        else "Dạ trong tầm giá của mình, em gợi ý: {danh_sach}. "
             "Anh/chị muốn em nói kỹ hơn máy nào không ạ?"
    )
    return {
        "text": ban_du_phong(bang, mau_du_phong),
        "nguon_llm": "ban_du_phong",
        "so_lan_bi_chan": c["so_lan_bat_viet_lai_toi_da"] + 1,
        "loi_da_chan": da_chan,
        "ms": tong_ms,
    }
