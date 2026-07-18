# -*- coding: utf-8 -*-
"""Che do GIAI THICH kien thuc dien may pho thong.

Khach hoi "X la gi / khac gi / co nen" -> tra loi bang KIEN THUC NGANH pho
thong (dung template co san, KHONG qua LLM -> khong bia thong so san pham).
Sau giai thich luon KEO VE nhu cau (sale gioi giai thich xong thi chot don).

Vi sao khong de LLM tu tra: LLM co the bia "Inverter tiet kiem 40% dien" - con
so khong co nguon. Template chi noi NGUYEN LY (dung/sai co the kiem chung), khong
gan con so cu the -> an toan tuyet doi.
"""
from __future__ import annotations

import re

from backend.app.core.chuan_hoa_tv import bo_dau

# tu khoa (khong dau) -> (giai thich, cau keo ve nhu cau)
_KIEN_THUC = [
    (r"inverter",
     "Máy Inverter chạy điều chỉnh công suất liên tục nên êm hơn và tốn ít điện "
     "hơn máy thường (non-Inverter) khi dùng lâu, đổi lại giá mua thường cao hơn. "
     "Máy non-Inverter rẻ hơn, hợp dùng ít giờ mỗi ngày.",
     "Anh chị định dùng nhiều giờ mỗi ngày không, và ngân sách khoảng bao nhiêu ạ?"),
    (r"\bhp\b|ngua|cong suat.*(?:la gi|nghia)",
     "HP (mã lực) là công suất làm lạnh của máy lạnh — chọn theo DIỆN TÍCH phòng "
     "chứ không theo số người: dưới 15m² ~1HP, 15–20m² ~1.5HP, 20–30m² ~2HP. "
     "Phòng có nắng chiếu thì lên một bậc.",
     "Phòng anh chị rộng khoảng bao nhiêu m² để em chọn đúng công suất ạ?"),
    (r"sao nang luong|nhan nang luong|may sao",
     "Số sao trên nhãn năng lượng cho biết mức tiết kiệm điện — càng nhiều sao "
     "càng ít tốn điện, nhưng giá máy thường cao hơn. Đây là nhãn do nhà nước dán, "
     "không phải đánh giá chất lượng tổng thể.",
     "Anh chị ưu tiên tiết kiệm điện hay ưu tiên giá rẻ hơn ạ?"),
    (r"dung tich tong|dung tich su dung|tong.*su dung",
     "Dung tích TỔNG là thể tích toàn tủ; dung tích SỬ DỤNG là phần thực sự chứa "
     "được đồ (đã trừ vách, dàn lạnh) — luôn nhỏ hơn. Khi so sức chứa thật thì "
     "nhìn dung tích sử dụng chính xác hơn.",
     "Nhà anh chị mấy người để em ước dung tích phù hợp ạ?"),
    (r"side.?by.?side|tu doi|multi.?door|ngan da (?:tren|duoi)",
     "Kiểu dáng tủ lạnh: Side by Side (2 cánh mở đôi, rộng, giá cao); Ngăn đá trên "
     "(phổ thông, rẻ); Ngăn đá dưới (lấy đồ mát tiện hơn); Multi Door (nhiều ngăn). "
     "Chọn theo diện tích bếp và thói quen dùng.",
     "Bếp nhà anh chị rộng cỡ nào và nhà mấy người ạ?"),
    (r"chong (?:giat|ro dien)|elcb",
     "ELCB là cầu dao chống rò điện — tự ngắt khi phát hiện dòng rò, tăng an toàn "
     "cho máy nước nóng. Nên ưu tiên khi nhà có trẻ nhỏ hoặc người lớn tuổi.",
     "Anh chị cần bình chứa bao nhiêu lít và ngân sách khoảng bao nhiêu ạ?"),
]


def giai_thich_kien_thuc(text: str) -> str | None:
    """Neu khach hoi kien thuc pho thong -> tra loi + cau keo ve nhu cau.
    Khong dinh -> None (flow tu van chay binh thuong).

    Chi kich hoat khi cau co DAU HIEU HOI KIEN THUC (la gi/khac gi/co nen/nghia
    la), tranh nham voi cau chon may binh thuong co chua tu 'inverter'."""
    kd = bo_dau(text or "").lower()
    if not re.search(r"\b(la gi|nghia la|khac (?:gi|nhau)|co nen|nen chon|the nao|"
                     r"ra sao|hieu (?:sao|nhu the nao)|giai thich)\b", kd):
        return None
    for mau, giai, keo in _KIEN_THUC:
        if re.search(mau, kd):
            return f"Dạ em giải thích nhanh ạ: {giai}\n\n{keo}"
    return None
