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
    (r"\bdb\b|do on",
     "Các số dB dạng 45/34/29 thường là mức ồn hãng công bố ở nhiều cấp vận "
     "hành; dạng 21–39 dB là một khoảng. Không nên lấy mức thấp nhất của máy "
     "này so với mức cao nhất của máy kia. Muốn kết luận máy nào êm hơn cần "
     "đối chiếu cùng dàn lạnh/dàn nóng, cùng chế độ và cùng điều kiện đo; nếu "
     "nguồn không ghi rõ thì chỉ có thể nêu giới hạn đó.",
     "Anh chị đang so đúng hai model nào để em kiểm tra các mức dB có nguồn ạ?"),
    (r"inverter",
     "Inverter là công nghệ điều chỉnh công suất thay vì chỉ bật/tắt theo một "
     "mức cố định. Chỉ nhãn Inverter chưa đủ để kết luận máy nào ít tốn điện "
     "hoặc êm hơn; cần so chỉ số điện năng, hiệu suất và độ ồn do hãng công bố "
     "trong cùng điều kiện.",
     "Anh chị định dùng nhiều giờ mỗi ngày không, và ngân sách khoảng bao nhiêu ạ?"),
    (r"\bhp\b|ngua|cong suat.*(?:la gi|nghia)",
     "HP (mã lực) là cách gọi mức công suất của máy lạnh. Khi chọn máy cần đối "
     "chiếu diện tích phòng với phạm vi sử dụng do hãng công bố; các yếu tố như "
     "nắng, nguồn nhiệt và độ kín phòng cũng làm thay đổi tải lạnh. Em không tự "
     "đặt ngưỡng HP khi chưa có bảng quy đổi được duyệt.",
     "Phòng anh chị rộng khoảng bao nhiêu m² để em chọn đúng công suất ạ?"),
    (r"sao nang luong|nhan nang luong|may sao",
     "Nhãn năng lượng cung cấp thông tin hiệu suất để tham khảo. Muốn kết luận "
     "máy nào tiết kiệm hơn cần so sản phẩm cùng loại, cùng công suất và cùng điều "
     "kiện thử; số sao không phải đánh giá chất lượng tổng thể.",
     "Anh chị ưu tiên tiết kiệm điện hay ưu tiên giá rẻ hơn ạ?"),
    (r"dung tich tong|dung tich su dung|tong.*su dung",
     "Dung tích TỔNG là thể tích toàn tủ; dung tích SỬ DỤNG là phần thực sự chứa "
     "được đồ sau khi tính các bộ phận bên trong. Khi so sức chứa thực tế nên ưu "
     "tiên cùng một loại chỉ số, thường là dung tích sử dụng do hãng công bố.",
     "Nhà anh chị mấy người để em ước dung tích phù hợp ạ?"),
    (r"side.?by.?side|tu doi|multi.?door|ngan da (?:tren|duoi)",
     "Đây là các kiểu bố trí cửa và ngăn khác nhau: Side by Side có hai cánh mở "
     "đôi; ngăn đá trên hoặc dưới mô tả vị trí ngăn đông; Multi Door có nhiều "
     "cửa/ngăn. Giá và kích thước phải đối chiếu từng mẫu trong catalog, không thể "
     "suy ra chỉ từ tên kiểu dáng.",
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
