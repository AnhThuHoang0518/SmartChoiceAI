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
from backend.app.schemas.ket_qua import BangKetQua, dong_so_sanh
from backend.app.schemas.nhu_cau import ONhuCauMayLanh, UuTien
from backend.app.services.llm import LLM

_LUAT_CHUNG = """Bạn là nhân viên tư vấn điện máy người Việt, xưng "em", gọi khách là "anh chị", kết câu bằng "ạ".

LUẬT TUYỆT ĐỐI:
1. CHỈ dùng số liệu có trong BẢNG KẾT QUẢ bên dưới. Không có số nào khác được xuất hiện.
2. Không dùng từ quảng cáo: "tốt nhất thị trường", "siêu phẩm", "đỉnh cao", "cực kỳ".
3. Không khen đều tất cả. Mỗi máy PHẢI nêu rõ được gì và MẤT gì.
4. Nếu bảng có mục "Không đề xuất", phải chủ động nói vì sao không đề xuất máy đó.
5. Tiêu chí khách đang ưu tiên phải được trả lời trực tiếp; không tự đổi trọng tâm sang tiêu chí khác.
6. TỐI ĐA 150 từ. Dài hơn là bị cắt.
7. Diễn đạt như người nói chuyện: "rẻ hơn", "đắt hơn nhưng được...", "êm hơn".
   TUYỆT ĐỐI không viết các cụm "Hơn về", "Kém về", "đối thủ".

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
        from backend.app.core.nhan_truong import tien_chu
        d.append(f"ngân sách tối đa {tien_chu(nhu_cau.ngan_sach_max)}")
    if nhu_cau.loai_phong:
        d.append("phòng ngủ" if nhu_cau.loai_phong.value == "ngu" else "phòng khách")
    if nhu_cau.uu_tien:
        d.append("ưu tiên: " + ", ".join(u.value for u in nhu_cau.uu_tien))
    if getattr(nhu_cau, "hang", None):
        d.append(f"chỉ xét hãng {nhu_cau.hang}")
    ci = getattr(nhu_cau, "can_inverter", None)
    if ci is not None:
        d.append("chỉ xét máy Inverter" if ci else "chỉ xét máy mono (non-Inverter)")

    ra = [", ".join(d), ""]
    ra.append(f"Đã lọc {bang.tong_truoc_loc} máy còn {bang.con_lai_sau_loc} máy phù hợp.")
    ra.append("")
    ra.append("TOP 3:")
    for i, u in enumerate(bang.top3, 1):
        ra.append(f"{i}. {u.ten} — giá {u.gia:,d}đ".replace(",", "."))
        for h in u.hon:
            ra.append(dong_so_sanh(h, la_hon=True))
        for k in u.kem:
            ra.append(dong_so_sanh(k, la_hon=False))
        if not u.hon and not u.kem:
            ra.append("   (ngang bằng các máy còn lại trên mọi tiêu chí khách quan tâm)")
        th = {n.truong: n.gia_tri for n in u.nguon}
        chi_tiet = []
        if giong == "ky_thuat" and th.get("pham_vi"):
            chi_tiet.append(f"dải {th['pham_vi']}")
        if (giong == "ky_thuat" or UuTien.DO_ON in nhu_cau.uu_tien) \
                and th.get("do_on_db") not in (None, "None"):
            chi_tiet.append(f"độ ồn {th['do_on_db']} dB")
        if (giong == "ky_thuat" or UuTien.TIET_KIEM_DIEN in nhu_cau.uu_tien) \
                and th.get("cspf") not in (None, "None"):
            chi_tiet.append(f"CSPF {th['cspf']}")
        if UuTien.LAM_LANH_NHANH in nhu_cau.uu_tien and th.get("lam_lanh_nhanh"):
            chi_tiet.append(f"làm lạnh nhanh: {th['lam_lanh_nhanh']}")
        if giong == "ky_thuat" and th.get("sao") not in (None, "None"):
            chi_tiet.append(f"{th['sao']} sao")
        if giong == "ky_thuat" and th.get("gia_goc") and str(th["gia_goc"]) != str(u.gia):
            chi_tiet.append(f"giá gốc {int(float(th['gia_goc'])):,d}đ".replace(",", "."))
        if chi_tiet:
            ra.append("   Thông tin đúng tiêu chí: " + " · ".join(chi_tiet))

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
    so_bia = 0                             # CHI dem hau kiem chan that
    tong_ms = 0

    for lan in range(c["so_lan_bat_viet_lai_toi_da"] + 1):
        try:
            text, ms = llm.sinh_do(he_thong, nguoi_dung)
        except Exception as e:              # noqa: BLE001
            # LLM chet giua chung (mang, het quota, server sap) -> khong duoc
            # 500 voi khach, NHUNG phai ghi ro ly do vao log thong ke - truoc
            # day nuot im va bi dem nham thanh "chan bia" (sai su that).
            text, ms = "", 0
            da_chan.append(f"LLM loi: {type(e).__name__}: {e}")
        tong_ms += ms
        if not text:
            break                                   # LuatLLM / LLM hong -> ban du phong

        loi = hau_kiem(text, bang, nhu_cau, c["dung_sai_tuong_doi"])
        if not loi:
            return {
                "text": text,
                "nguon_llm": llm.ten,
                "so_lan_bi_chan": so_bia,
                "loi_da_chan": da_chan,
                "ms": tong_ms,
            }

        so_bia += 1
        da_chan += loi
        # TRAN THOI GIAN: da ton >6s ma con phai viet lai -> ve ban du phong
        # luon, dung bat khach doi them 5s nua (moc de bai <5s; do that co luot
        # 12.5s vi 2 vong viet lai voi model suy luan cham).
        if tong_ms > 6000:
            da_chan.append("qua tran 6s - ve ban du phong thay vi viet lai")
            break
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
        else "Dạ trong tầm giá của anh chị, em gợi ý: {danh_sach}. "
             "Anh/chị muốn em nói kỹ hơn máy nào không ạ?"
    )
    return {
        "text": ban_du_phong(bang, mau_du_phong),
        "nguon_llm": "ban_du_phong",
        "so_lan_bi_chan": so_bia,
        "loi_da_chan": da_chan,
        "ms": tong_ms,
    }
