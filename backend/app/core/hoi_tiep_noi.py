# -*- coding: utf-8 -*-
"""Cau hoi tiep noi duoc tra bang CODE tu bang ket qua da co nguon.

LLM khong duoc nhin lich su de tu doan "no", "tu nao" hay y nghia badge.
Module nay chi lam ba viec huu han, giai trinh duoc:
  - nhan dien cau hoi so sanh dien nang tren top vua hien;
  - giai thich ten truong ky thuat;
  - ghi nhan tieu chi may lanh ma catalog hien khong co.
"""
from __future__ import annotations

import re

from backend.app.core.chuan_hoa_tv import bo_dau


_GIAI_THICH_TRUONG: tuple[tuple[str, str], ...] = (
    (
        r"\b(?:sau|chieu sau)\s+(?:la|nghia la|tinh tu|do tu).*(?:gi|dau|nao)\b",
        "Dạ **sâu** là khoảng cách từ mặt trước đến mặt sau của sản phẩm, "
        "được ghi theo cm. Đây là kích thước thân máy do catalog công bố; "
        "nếu chỗ đặt có giới hạn, anh chị nên đối chiếu thêm khoảng hở lắp đặt "
        "theo hướng dẫn của hãng ạ.",
    ),
    (
        r"\b(?:ngang|chieu ngang)\s+(?:la|nghia la|tinh tu|do tu).*(?:gi|dau|nao)\b",
        "Dạ **ngang** là khoảng cách từ cạnh trái sang cạnh phải của sản phẩm, "
        "được ghi theo cm ạ.",
    ),
    (
        r"\b(?:cao|chieu cao)\s+(?:la|nghia la|tinh tu|do tu).*(?:gi|dau|nao)\b",
        "Dạ **cao** là khoảng cách từ đáy đến điểm cao nhất của sản phẩm, "
        "được ghi theo cm ạ.",
    ),
    (
        r"\b(?:dien nang|kwh)\s+(?:la|nghia la).*(?:gi|sao)\b",
        "Dạ **điện năng** là lượng điện sản phẩm tiêu thụ trong một khoảng "
        "thời gian. Khi cùng cách đo và cùng đơn vị, số kWh thấp hơn nghĩa là "
        "tiêu thụ ít điện hơn ạ.",
    ),
    (
        r"\bcspf\s+(?:la|nghia la).*(?:gi|sao)\b",
        "Dạ **CSPF** là chỉ số hiệu suất năng lượng của máy lạnh theo mùa. "
        "Khi so trong cùng cách công bố, CSPF cao hơn thể hiện hiệu suất sử dụng "
        "điện tốt hơn; đây không phải số điện tiêu thụ tuyệt đối ạ.",
    ),
)


def giai_thich_truong(text: str) -> str | None:
    """Tra dinh nghia field hien tren badge; khong gan gia tri cho san pham."""
    kd = bo_dau(text or "").lower()
    for mau, tra_loi in _GIAI_THICH_TRUONG:
        if re.search(mau, kd):
            return tra_loi
    return None


def _hoi_may_nao_it_ton_dien(text: str) -> bool:
    kd = bo_dau(text or "").lower()
    tieu_chi = r"(?:it\s+ton\s+dien|tiet\s+kiem\s+dien|ton\s+dien\s+it)"
    return bool(
        re.search(rf"\b(?:tu|may|cai|con)?\s*nao\b.{{0,35}}{tieu_chi}", kd)
        or re.search(rf"{tieu_chi}.{{0,35}}\b(?:nao|nhat|hon)\b", kd)
        or re.search(r"\bso sanh\b.{0,25}\b(?:dien nang|tieu thu dien)\b", kd)
    )


_QUY_TAC_DIEN = {
    "may_lanh": ("cspf", False, "CSPF", ""),
    "tu_lanh": ("dien_kwh_nam", True, "điện năng", " kWh/năm"),
    "tu_dong_mat": ("dien_kwh_ngay", True, "điện năng", " kWh/ngày"),
    "may_giat": ("dien_wh_kg", True, "điện năng", " Wh/kg"),
}


def _so(nguon: list[dict], truong: str) -> float | None:
    for n in nguon or []:
        if n.get("truong") != truong:
            continue
        v = n.get("gia_tri")
        if v in (None, "", "None"):
            return None
        try:
            return float(str(v).replace(",", "."))
        except ValueError:
            return None
    return None


def _so_chu(v: float) -> str:
    return f"{v:g}".replace(".", ",")


def tra_loi_tiet_kiem_dien(
    text: str, top3: list[dict], nganh: str | None
) -> tuple[str, str] | None:
    """Tra (text, truong_da_doi_chieu), chi khi co cau hoi tiep noi ro rang.

    Neu mot san pham thieu field thi khong tuyen bo quan quan. Tat ca so deu
    doc tu ``nguon`` da luu trong bang top truoc, khong doc lai catalog va
    khong cho LLM chen so.
    """
    if not top3 or not _hoi_may_nao_it_ton_dien(text):
        return None

    quy_tac = _QUY_TAC_DIEN.get(nganh or "")
    if quy_tac is None:
        # Chon field tieu thu co don vi that neu nganh moi co no. Khong dung
        # cong suat W thay cho dien nang vi hai khai niem khac nhau.
        for ung in (
            ("dien_kwh_ngay", True, "điện năng", " kWh/ngày"),
            ("dien_kwh_nam", True, "điện năng", " kWh/năm"),
            ("dien_wh_kg", True, "điện năng", " Wh/kg"),
        ):
            if any(_so(u.get("nguon", []), ung[0]) is not None for u in top3):
                quy_tac = ung
                break
    if quy_tac is None:
        return (
            "Dạ dữ liệu nguồn của các sản phẩm vừa xem chưa có trường điện năng "
            "tiêu thụ có thể đối chiếu, nên em chưa thể kết luận máy nào ít tốn "
            "điện hơn ạ.",
            "",
        )

    truong, thap_tot, nhan, don_vi = quy_tac
    co, thieu = [], []
    for u in top3:
        v = _so(u.get("nguon", []), truong)
        (co if v is not None else thieu).append((u.get("ten", "Sản phẩm"), v))

    so_da_co = " · ".join(
        f"{ten}: {_so_chu(v)}{don_vi}" for ten, v in co if v is not None
    )
    if thieu:
        ten_thieu = ", ".join(ten for ten, _ in thieu)
        them = f" Số có nguồn: {so_da_co}." if so_da_co else ""
        return (
            f"Dạ em chưa thể chốt sản phẩm nào ít tốn điện nhất vì {ten_thieu} "
            f"chưa có {nhan} trong dữ liệu nguồn.{them}",
            truong,
        )

    gia_tri = [v for _, v in co if v is not None]
    if len(set(gia_tri)) == 1:
        return (
            f"Dạ các sản phẩm vừa xem có cùng {nhan} hãng công bố: "
            f"{_so_chu(gia_tri[0])}{don_vi}. Vì vậy chưa có máy nào hơn về tiêu "
            "chí này ạ.",
            truong,
        )

    tot = (min if thap_tot else max)(co, key=lambda x: x[1])
    if truong == "cspf":
        mo_ta = (
            f"**{tot[0]}** có CSPF cao nhất: **{_so_chu(tot[1])}**. "
            "CSPF cao hơn thể hiện hiệu suất năng lượng tốt hơn, nhưng không phải "
            "số điện tiêu thụ tuyệt đối."
        )
    else:
        mo_ta = (
            f"**{tot[0]}** có {nhan} hãng công bố thấp nhất: "
            f"**{_so_chu(tot[1])}{don_vi}**."
        )
    return f"Dạ {mo_ta} Các số đang đối chiếu: {so_da_co} ạ.", truong


def tieu_chi_may_lanh_chua_co_nguon(text: str) -> set[str]:
    """Field khach co nhac nhung catalog may lanh chua nap duoc."""
    kd = bo_dau(text or "").lower()
    ra = set()
    if re.search(r"\b(?:tre nho|tre em|em be|so sinh)\b", kd):
        ra.add("tre_nho")
    if re.search(r"\b(?:nhiet do|dai nhiet|bao nhieu do c|chinh may do)\b", kd):
        ra.add("nhiet_do")
    return ra


def canh_bao_may_lanh_chua_co_nguon(cac_tieu_chi: set[str] | list[str]) -> str:
    ds = set(cac_tieu_chi or [])
    thieu = []
    if "tre_nho" in ds:
        thieu.append("chế độ riêng cho trẻ nhỏ")
    if "nhiet_do" in ds:
        thieu.append("dải nhiệt độ cài đặt của từng máy")
    if not thieu:
        return ""
    return (
        "Dạ em lưu ý trước: catalog hiện chưa có trường " + " và ".join(thieu)
        + ". Em chưa dùng các tiêu chí này để khẳng định máy phù hợp; kết quả "
        "bên dưới chỉ dựa trên những thông số có nguồn ạ."
    )
