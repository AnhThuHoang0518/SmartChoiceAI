# -*- coding: utf-8 -*-
"""NHU CAU GIAN TIEP: khach noi TINH HUONG/VAN DE thay vi ten san pham.

Vd "tóc bị ướt cần mua gì" -> máy sấy tóc; "nhà nóng quá" -> máy lạnh;
"quần áo lâu khô mùa mưa" -> máy sấy; "đồ ăn hay hỏng" -> tủ lạnh.

Day la HIEU Y (NLU) chu khong phai bia: anh xa tinh huong -> LOAI san pham.
- San pham suy ra CO du lieu (14 nganh) -> goi y nganh do (khach van xac nhan).
- San pham suy ra KHONG co du lieu (may say toc, quat, loa...) -> tu choi that
  tha, khong day khach sang nganh gan gan sai (may say toc != may say quan ao).

Chay bang LUAT: tin cay, 0ms, giai trinh duoc. Embedding (hieu_y_mo) lam lop
vot khi luat khong dinh.
"""
from __future__ import annotations

import re

from backend.app.core.chuan_hoa_tv import bo_dau

# (mau tinh huong, ten hien thi nganh CO du lieu). Thu tu: cu the truoc.
_TINH_HUONG_CO_DATA: list[tuple[str, str]] = [
    (r"nha nong|phong nong|nong qua|oi buc|oi a|nong nuc|khong khi nong", "máy lạnh"),
    (r"do an .*(?:hong|oi|thiu|hu)|thuc pham .*(?:hong|bao quan)|rau .*heo|giu do an|do an de lau", "tủ lạnh"),
    (r"tru dong|dong da|nhieu (?:thit|ca|kem)|ban do dong lanh|dong lanh nhieu", "tủ đông"),
    (r"quan ao .*(?:lau kho|am|moc|khong kho)|mua mua|troi nom|do khong kho", "máy sấy"),
    (r"giat .*(?:met|nhieu do|quan ao ban)|nhieu quan ao ban|do ban nhieu", "máy giặt"),
    (r"rua (?:bat|chen) .*met|nhieu (?:bat|chen)|ngai rua bat|rua chen met", "máy rửa chén"),
    (r"tam .*(?:nuoc lanh|lanh run|nuoc nong)|khong co nuoc nong|nuoc lanh qua", "máy nước nóng"),
    (r"in .*(?:tai lieu|giay to|van ban|hop dong)|can in\b|muon in\b", "máy in"),
    (r"hat karaoke|hat ho|thu am|livestream", "micro"),
    (r"hoc online|hoc bai .*(?:online|may)|xem phim cam tay|doc sach dien tu", "máy tính bảng"),
    (r"deo tay .*(?:suc khoe|the thao|chay bo)|dem buoc|do nhip tim", "đồng hồ thông minh"),
]

# (mau tinh huong, ten san pham KHONG co du lieu) -> tu choi that tha
_TINH_HUONG_NGOAI: list[tuple[str, str]] = [
    (r"toc .*(?:uot|am|kho)|say toc|lam kho toc|so toc", "máy sấy tóc"),
    (r"nghe nhac to|loa .*(?:keo|bluetooth|nghe nhac)|am thanh to", "loa"),
    (r"loc .*(?:nuoc|khong khi)|nuoc ban|khong khi o nhiem|bui min", "máy lọc"),
    (r"nau com|com song|hap com", "nồi cơm điện"),
    (r"quat .*mat|lam mat .*(?:khong dieu hoa|re)", "quạt"),
]


def nhu_cau_gian_tiep(text: str) -> tuple[str, str] | None:
    """Tra ('nganh', ten) neu tinh huong suy ra san pham CO du lieu;
    ('ngoai', ten_san_pham) neu suy ra san pham KHONG co du lieu;
    None neu khong nhan ra tinh huong nao."""
    kd = bo_dau(text or "").lower()
    for mau, sp in _TINH_HUONG_NGOAI:          # ngoai xet truoc: 'toc uot' ro rang
        if re.search(mau, kd):
            return ("ngoai", sp)
    for mau, nganh in _TINH_HUONG_CO_DATA:
        if re.search(mau, kd):
            return ("nganh", nganh)
    return None
