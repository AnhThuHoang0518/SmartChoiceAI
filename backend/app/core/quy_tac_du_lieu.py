# -*- coding: utf-8 -*-
"""Tra loi cac yeu cau can thiep vao quy tac du lieu bang CODE.

Day khong phai intent tu van san pham. Nguoi dung co the yeu cau coi null la
0, quang cao cap gia nguoc, hoac hoi do tuoi gia. He thong phai noi ro hang
rao dang ap dung thay vi dua cau nay cho LLM hay router nganh.
"""
from __future__ import annotations

import re

from backend.app.core.chuan_hoa_tv import bo_dau


def tra_loi_quy_tac_du_lieu(text: str) -> tuple[str, str] | None:
    """Tra ``(ma_quy_tac, cau_tra_loi)`` neu cau noi dung hang rao du lieu."""
    kd = bo_dau(text or "").lower()

    if re.search(r"\b(?:bo qua|phớt lờ|phot lo)\b.{0,30}\b(?:catalog|nguon|bang diem|ranking)\b", kd):
        return "giu_nguon_xep_hang", (
            "Dạ em không thể bỏ qua catalog, nguồn dữ liệu hoặc bảng điểm để "
            "khen một sản phẩm theo yêu cầu ạ. Em chỉ xếp hạng từ tiêu chí anh "
            "chị nêu và dữ liệu có nguồn; nếu thiếu dữ liệu em sẽ nói rõ."
        )

    if re.search(r"\binverter\b", kd) and re.search(
        r"(?:chac chan|mac dinh).{0,25}(?:it ton dien|tiet kiem dien)|"
        r"(?:it ton dien|tiet kiem dien).{0,25}(?:chac chan|nhat)", kd
    ):
        return "inverter_khong_du_bang_chung", (
            "Dạ chỉ có nhãn Inverter chưa đủ để kết luận sản phẩm ít tốn điện "
            "nhất ạ. Em chỉ so khi có điện năng/hiệu suất cùng đơn vị và giữa "
            "các sản phẩm có quy mô sử dụng tương đương; thiếu số đó em sẽ không chốt."
        )

    if "dung tich tong" in kd and "dung tich su dung" in kd:
        return "dung_tich_tong_va_su_dung", (
            "Dạ khi nói sức chứa thực tế, em ưu tiên dung tích sử dụng ạ. Dung "
            "tích tổng có thể gồm cả phần kết cấu/không gian không sử dụng trực "
            "tiếp; em không cộng các ngăn để tự tạo một con số mới. Nếu model "
            "chỉ công bố dung tích tổng, em sẽ ghi rõ giới hạn đó."
        )

    if re.search(r"(?:tru|bao quan).{0,20}(?:thit|ca)", kd) \
            and re.search(r"ra dong|dong mem|ngan chuyen doi", kd):
        return "bao_quan_tu_lanh_thieu_nguon", (
            "Dạ catalog tủ lạnh hiện chưa nạp trường công nghệ bảo quản/đông "
            "mềm và dung tích ngăn chuyển đổi, nên em chưa thể đề xuất model "
            "theo yêu cầu rã đông nhanh ạ. Em không suy tính năng này từ tên "
            "hãng, giá hay dung tích ngăn đá."
        )

    if re.search(r"(?:khong co|thieu|null).{0,25}gia", kd) \
            and re.search(r"(?:re nhat|gia 0|bang 0|coi.*re)", kd):
        return "gia_thieu", (
            "Dạ em không coi sản phẩm thiếu giá là giá 0 hay rẻ nhất ạ. "
            "Sản phẩm không có giá hợp lệ sẽ bị loại khỏi lọc giá và xếp hạng; "
            "em sẽ nói rõ là thiếu dữ liệu thay vì đoán."
        )

    if re.search(r"gia khuyen mai.{0,30}(?:cao|lon|dat).{0,20}gia goc", kd):
        return "gia_mau_thuan", (
            "Dạ đây là cặp giá bất thường, nên em không hiển thị là khuyến mãi "
            "và không tạo phần trăm giảm ạ. Khi chưa có API giá chính thức để "
            "đối chiếu, hệ thống dùng giá gốc làm mức tham khảo và gắn nguồn tệp dữ liệu."
        )

    if "model_code" in kd and "sku" in kd \
            and re.search(r"(?:cung|trung).{0,15}model_code", kd):
        return "dinh_danh_bien_the", (
            "Dạ em không gộp hai dòng chỉ vì cùng model_code ạ. SKU hoặc "
            "productidweb là định danh biến thể; nếu giá hay thông số khác nhau, "
            "chúng vẫn là hai sản phẩm riêng trong catalog."
        )

    if all(x in kd for x in ("khong", "hang khong cong bo", "dang cap nhat")) \
            and ("null" in kd or "field" in kd):
        return "phan_loai_thieu", (
            "Dạ hệ thống phân biệt hai trạng thái ạ: “Không/Không có” là phủ "
            "định thật khi trường đó cho phép giá trị có/không; còn “Hãng không "
            "công bố”, “Đang cập nhật” và null là chưa biết. Giá trị chưa biết "
            "không được dùng để lọc hoặc khẳng định tính năng."
        )

    if "updated_at" in kd or re.search(
        r"gia.{0,30}(?:khong co|thieu).{0,20}(?:thoi diem|ngay cap nhat)", kd
    ):
        return "gia_thieu_thoi_diem", (
            "Dạ nguồn giá hiện chưa có updated_at chính thức, nên em không gọi "
            "đây là giá hiện tại hay giá hôm nay ạ. Giao diện chỉ hiển thị mức "
            "giá từ catalog cùng nguồn và thời điểm tệp dữ liệu được cập nhật; "
            "anh chị nên kiểm tra lại giá bán trước khi mua."
        )

    return None
