# -*- coding: utf-8 -*-
"""Tra loi cau hoi chinh sach tu tai lieu PRIVATE nap luc runtime.

Repo public khong duoc chua tai lieu that cua doi tac. Vi vay module nay chi
chua CODE tim kiem va trich doan; noi dung that nam ngoai git o:

    data/policies/*.md

hoac thu muc do bien moi truong `CHINH_SACH_DIR` tro toi. Khong dung LLM: cau
tra loi chinh sach la lay tu tai lieu da nap, thieu thi noi thang.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from backend.app.core.chuan_hoa_tv import bo_dau


THU_MUC_MAC_DINH = Path("data/policies")
SO_KY_TU_TOI_DA = 1400


@dataclass(frozen=True)
class DoanChinhSach:
    tep: str
    tieu_de: str
    text: str


_TEN_TEP_UU_TIEN = {
    "bao_hanh_doi_tra": ("bao hanh", "doi tra", "hoan tien", "hu gi doi nay", "loi ky thuat"),
    "giao_hang_lap_dat": ("giao hang", "lap dat", "van chuyen", "phi giao", "thoi gian giao"),
    "khui_hop_apple": ("khui hop", "apple", "iphone", "ipad", "macbook"),
    "du_lieu_ca_nhan": ("du lieu ca nhan", "rieng tu", "bao mat thong tin", "thong tin ca nhan"),
    "dieu_khoan_su_dung": ("dieu khoan", "su dung website", "quy dinh website"),
    "noi_quy_cua_hang": ("noi quy", "cua hang", "sieu thi"),
    "chat_luong_phuc_vu": ("tong dai", "phuc vu", "khieu nai", "ho tro online"),
}

_NHAN_TEP = {
    "chat_luong_phuc_vu.md": "Chất lượng phục vụ online",
    "chinh_sach_bao_hanh_doi_tra.md": "Chính sách bảo hành/đổi trả",
    "chinh_sach_giao_hang_lap_dat.md": "Chính sách giao hàng/lắp đặt",
    "chinh_sach_khui_hop_apple.md": "Chính sách khui hộp Apple",
    "chinh_sach_xu_ly_du_lieu_ca_nhan.md": "Chính sách xử lý dữ liệu cá nhân",
    "dieu-khoang-su-dung.md": "Điều khoản sử dụng",
    "noi_quy_cua_hang.md": "Nội quy cửa hàng",
}


def _thu_muc() -> Path:
    return Path(os.getenv("CHINH_SACH_DIR") or os.getenv("POLICY_DIR") or THU_MUC_MAC_DINH)


def _doc_teps() -> list[Path]:
    d = _thu_muc()
    if not d.exists():
        return []
    return sorted(p for p in d.glob("*.md") if p.is_file())


def _tach_doan(tep: Path, raw: str) -> list[DoanChinhSach]:
    """Tach markdown/plain text thanh cac doan vua du de tra loi.

    Tai lieu crawl tu web co khi khong dung heading markdown, nen tach theo dong
    in hoa/ngan + khoang trang. Day la parser co chu dich, khong bien thanh RAG
    tu do dung LLM.
    """
    dong = [x.strip() for x in raw.replace("\r\n", "\n").split("\n")]
    ds: list[DoanChinhSach] = []
    tieu_de = tep.stem.replace("_", " ")
    dem: list[str] = []

    def flush() -> None:
        nonlocal dem
        text = "\n".join(x for x in dem if x).strip()
        if text:
            ds.append(DoanChinhSach(tep.name, tieu_de, text))
        dem = []

    for line in dong:
        la_heading_md = line.startswith("#")
        kd = bo_dau(line).strip()
        la_heading_text = (
            4 <= len(kd) <= 90
            and not line.endswith((".", ",", ";", ":"))
            and (
                line.isupper()
                or bool(re.match(r"^\d+[\).]?\s*[A-ZÀ-ỸĐ]", line))
                or kd.lower().startswith(("noi dung", "dieu kien", "luu y", "phi ", "thoi gian"))
            )
        )
        if la_heading_md or la_heading_text:
            flush()
            tieu_de = re.sub(r"^#+\s*", "", line).strip() or tieu_de
        else:
            dem.append(line)
            if sum(len(x) for x in dem) >= 900:
                flush()
    flush()
    return ds


@lru_cache(maxsize=1)
def _kho_doan() -> tuple[DoanChinhSach, ...]:
    ds: list[DoanChinhSach] = []
    for tep in _doc_teps():
        try:
            ds.extend(_tach_doan(tep, tep.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            ds.extend(_tach_doan(tep, tep.read_text(encoding="utf-8-sig")))
    return tuple(ds)


def xoa_cache_chinh_sach() -> None:
    """Dung khi vua scp/cap nhat file policy trong tien trinh dang chay."""
    _kho_doan.cache_clear()


def hoi_chinh_sach(text: str) -> bool:
    """Nhan biet cau hoi chinh sach/dich vu, tranh dinh cau hoi spec san pham.

    Vi du "may giat bao hanh dong co lau khong" la spec ranking, khong phai
    chinh sach doi tra. Con "chinh sach bao hanh/doi tra the nao" thi bat.
    """
    kd = bo_dau(text or "").lower()
    if not kd.strip():
        return False
    mau_ro = (
        r"\b(chinh sach|doi tra|doi moi|tra hang|hoan tien|loi ky thuat|"
        r"hu gi doi nay|giao hang|lap dat|van chuyen|phi giao|phi lap|"
        r"khui hop|du lieu ca nhan|bao mat thong tin|dieu khoan su dung|"
        r"noi quy cua hang|tong dai|khieu nai|cham soc khach hang)\b"
    )
    if re.search(mau_ro, kd):
        return True
    # "bao hanh" don le chi coi la chinh sach neu khong dang hoi truc tiep ve
    # thong so/bao hanh dong co cua san pham.
    if "bao hanh" in kd and not re.search(r"\b(dong co|may nao|hang nao|lau hon|tot hon|ben hon)\b", kd):
        return True
    return False


def _diem_ten_tep(tep: str, cau: str) -> int:
    ten = bo_dau(tep).lower().replace("-", "_")
    diem = 0
    for nhan, tu_khoa in _TEN_TEP_UU_TIEN.items():
        if nhan in ten and any(t in cau for t in tu_khoa):
            diem += 8
    return diem


def _tu_khoa_noi_dung(cau: str) -> set[str]:
    bo = {
        "anh", "chi", "em", "toi", "minh", "cho", "hoi", "nhe", "nha", "duoc",
        "khong", "ko", "k", "co", "la", "ve", "thi", "the", "nao", "may",
    }
    return {w for w in re.findall(r"[a-z0-9]{3,}", cau) if w not in bo}


def _diem(doan: DoanChinhSach, cau: str, tu_khoa: set[str]) -> int:
    nd = bo_dau(f"{doan.tep} {doan.tieu_de} {doan.text}").lower()
    diem = _diem_ten_tep(doan.tep, cau)
    diem += sum(3 for t in tu_khoa if t in nd)
    # Uu tien doan co tieu de khop truc tiep voi cau hoi.
    td = bo_dau(doan.tieu_de).lower()
    diem += sum(4 for t in tu_khoa if t in td)
    return diem


def _rut_gon(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = re.sub(r"[ \t]{2,}", " ", text)
    if len(text) <= SO_KY_TU_TOI_DA:
        return text
    cat = text[:SO_KY_TU_TOI_DA].rsplit("\n", 1)[0].strip()
    return (cat or text[:SO_KY_TU_TOI_DA].strip()) + "\n…"


def tra_loi_chinh_sach(text: str) -> dict:
    """Tra dict de router dua thang ve TraLoi.

    `cham_llm` luon 0: khong goi LLM, khong suy dien ngoai tai lieu.
    """
    ds = _kho_doan()
    if not ds:
        return {
            "loai": "thieu_du_lieu_chinh_sach",
            "text": (
                "Dạ hiện hệ thống chưa được nạp tài liệu chính sách nên em chưa trả lời "
                "chắc được ạ. Anh chị có thể liên hệ tổng đài Điện máy XANH; khi có "
                "tài liệu chính sách chính thức được nạp, em sẽ tra cứu lại đúng nguồn."
            ),
            "nguon": [],
        }

    cau = bo_dau(text or "").lower()
    tu_khoa = _tu_khoa_noi_dung(cau)
    xep = sorted(((_diem(d, cau, tu_khoa), d) for d in ds), key=lambda x: x[0], reverse=True)
    chon = [d for diem, d in xep[:3] if diem > 0]
    if not chon:
        return {
            "loai": "khong_tim_thay_chinh_sach",
            "text": (
                "Dạ em có tài liệu chính sách nhưng chưa tìm thấy đoạn khớp với câu hỏi "
                "này ạ. Anh chị hỏi cụ thể hơn giúp em, ví dụ: đổi trả, bảo hành, "
                "giao hàng/lắp đặt, khui hộp Apple hoặc dữ liệu cá nhân."
            ),
            "nguon": [],
        }

    dong = ["Dạ em tra theo tài liệu chính sách đã nạp và thấy phần liên quan như sau ạ:"]
    nguon = []
    da_them: set[tuple[str, str, str]] = set()
    for d in chon:
        khoa = (d.tep, d.tieu_de, d.text[:80])
        if khoa in da_them:
            continue
        da_them.add(khoa)
        nguon.append({"tep": d.tep, "tieu_de": d.tieu_de})
        tieu_de = d.tieu_de if d.tieu_de and d.tieu_de != d.tep else _NHAN_TEP.get(d.tep, d.tep)
        if tieu_de == d.tep.replace(".md", "").replace("_", " "):
            tieu_de = _NHAN_TEP.get(d.tep, tieu_de)
        dong.append(f"\n**{tieu_de}**")
        dong.append(_rut_gon(d.text))
    dong.append("\nAnh chị cho em biết sản phẩm/đơn hàng cụ thể nếu cần em đối chiếu kỹ hơn theo đúng nhóm chính sách ạ.")
    return {"loai": "chinh_sach", "text": "\n".join(dong), "nguon": nguon}
