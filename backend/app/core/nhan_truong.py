# -*- coding: utf-8 -*-
"""Ten truong ky thuat -> nhan tieng Viet + don vi (UI badge & bang so sanh).

Mot cho duy nhat: them nganh moi thi them nhan o day, UI tu an theo (frontend
lay qua /api/nhan-truong luc tai trang - khong hardcode 2 noi).
"""

# truong -> (nhan hien thi, don vi ghep sau gia tri)
NHAN: dict[str, tuple[str, str]] = {
    "gia": ("Giá", "đ"),
    "gia_goc": ("Giá gốc", "đ"),
    "hang": ("Hãng", ""),
    "qua": ("Quà tặng", ""),
    # may lanh
    "pham_vi": ("Phạm vi phòng", ""),
    "do_on_db": ("Độ ồn", " dB"),
    "cspf": ("Hiệu suất CSPF", ""),
    "sao": ("Sao năng lượng", " sao"),
    # tu lanh / tu dong mat
    "nguoi_phu_hop": ("Số người dùng", ""),
    "dung_tich_lit": ("Dung tích", " lít"),
    "dung_tich_min": ("Dung tích tối thiểu", " lít"),
    "dien_kwh_nam": ("Điện năng", " kWh/năm"),
    "dien_kwh_ngay": ("Điện năng", " kWh/ngày"),
    "ngang_cm": ("Ngang", " cm"),
    "cao_cm": ("Cao", " cm"),
    "sau_cm": ("Sâu", " cm"),
    "kieu_dang": ("Kiểu dáng", ""),
    "so_cua": ("Số cửa", ""),
    # may giat / say
    "nguoi_min": ("Số người (từ)", ""),
    "nguoi_max": ("Số người (đến)", ""),
    "tai_kg": ("Khối lượng giặt/sấy", " kg"),
    "dien_wh_kg": ("Điện năng", " Wh/kg"),
    "vat_vong": ("Tốc độ vắt", " vòng/phút"),
    "bao_hanh_dc_nam": ("Bảo hành động cơ", " năm"),
    "dien_w": ("Công suất", " W"),
    "nhiet_toi_da_c": ("Nhiệt sấy tối đa", "°C"),
    "loai": ("Loại", ""),
    # may rua chen
    "bua_min": ("Số bữa (từ)", ""),
    "bua_max": ("Số bữa (đến)", ""),
    "bo_chau_au": ("Bộ chén đĩa (chuẩn Âu)", " bộ"),
    "nuoc_lit": ("Nước mỗi lần rửa", " lít"),
    # may nuoc nong
    "cong_suat_w": ("Công suất", " W"),
    "an_toan": ("An toàn", ""),
    # dien tu
    "man_inch": ("Màn hình", " inch"),
    "ram_gb": ("RAM", " GB"),
    "luu_tru_gb": ("Bộ nhớ", " GB"),
    "ssd_gb": ("Ổ cứng", " GB"),
    "pin_mah": ("Pin", " mAh"),
    "pin_ngay": ("Pin", " ngày"),
    "pin_gio": ("Pin", " giờ"),
    "nang_g": ("Cân nặng", " g"),
    "sim": ("SIM", ""),
    "nghe_goi": ("Nghe gọi", ""),
    "khang_nuoc": ("Kháng nước", ""),
    "dap_ung_ms": ("Đáp ứng", " ms"),
    "do_sang_nit": ("Độ sáng", " nit"),
    "phan_giai": ("Độ phân giải", ""),
    "tam_nen": ("Tấm nền", ""),
    "cpu": ("CPU", ""),
    "toc_do_trang": ("Tốc độ in", " trang/phút"),
    "ket_noi": ("Kết nối", ""),
    "binh_lit": ("Bình chứa", " lít"),
    "ngan_da_lit": ("Ngăn đá", " lít"),
    "phu_mau_pct": ("Độ phủ màu", "%"),
    "khay_to": ("Khay nạp giấy", " tờ"),
    "cong_suat_thang": ("Công suất in", " trang/tháng"),
    "loa_co": ("Loa tích hợp", ""),
    "cong_nghe_cpu": ("Dòng CPU", ""),
    # micro
    "khoang_cach_m": ("Khoảng cách truyền", " m"),
    "nhom": ("Nhóm", ""),
}


def dinh_dang(truong: str, gia_tri: str) -> tuple[str, str]:
    """Tra (nhan, gia tri da ghep don vi). Tien thi cham nghin kieu VN."""
    nhan, dv = NHAN.get(truong, (truong, ""))
    v = str(gia_tri)
    if dv == "đ":
        try:
            v = f"{int(float(v)):,d}".replace(",", ".")
        except ValueError:
            pass
    elif v.endswith(".0"):
        v = v[:-2]
    return nhan, v + dv
