# -*- coding: utf-8 -*-
"""Nganh TU LANH - vertical thu 2, chung minh cau "them nganh = them config".

Tai dung nguyen: hau_kiem (da co ro lit/kwh/cm/nguoi), viet_lai (qua
mo_ta_nhu_cau), phien, chuan hoa tieng Viet, UI. Rieng cua nganh: o nhu cau,
loc cung, cham diem - vi tri thuc nganh khac nhau that su.

Truc chon theo DO PHU DO DUOC tren 1.692 dong that (khong doan):
  So nguoi su dung (74%, hang cong bo) -> LOC CUNG - vai giong 'Pham vi su dung'
  Dung tich su dung (66%, roi ve tong 80% co danh dau) -> suc chua (TC-006)
  Dien nang kWh/nam (76%, so THAT)     -> tiet kiem dien, thap = tot
  Ngang/Cao/Sau (33%)                  -> loc hoc bep; thieu thi NOI, khong doan
  Kieu dang (96%)                      -> side by side / mini / ngan da tren-duoi
"""
from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from enum import Enum
from typing import ClassVar
from pathlib import Path

from pydantic import BaseModel, Field

from backend.app.core.chuan_hoa_tv import bo_dau, chuan_hoa
from backend.app.schemas.ket_qua import (
    BangKetQua,
    LyDoLoai,
    Nguon,
    TrucSoSanh,
    UngVien,
    dong_so_sanh,
)

MAC_DINH = Path("data/processed/tu_lanh.csv")
DU_PHONG_MAU = Path("data/mock/catalog/tu_lanh_mau.csv")


# ── O nhu cau ───────────────────────────────────────────────────────────────

class UuTienTL(str, Enum):
    TIET_KIEM_DIEN = "tiet_kiem_dien"
    DUNG_TICH = "dung_tich"
    GIA = "gia"


class ONhuCauTuLanh(BaseModel):
    ngan_sach_max: int | None = None
    so_nguoi: int | None = Field(None, description="TC-001: map so nguoi -> dai hang cong bo")
    ngang_cm: float | None = Field(None, description="TC-002: hoc bep - loc cung")
    cao_cm: float | None = None
    sau_cm: float | None = None
    kieu_dang: str | None = Field(None, description="TC-005: side by side / mini...")
    hang: str | None = None
    uu_tien: list[UuTienTL] = Field(default_factory=list)

    O_BAT_BUOC: ClassVar[tuple] = ("so_nguoi", "ngan_sach_max")

    def thieu_bat_buoc(self) -> list[str]:
        return [o for o in self.O_BAT_BUOC if getattr(self, o) is None]


# ── Catalog ─────────────────────────────────────────────────────────────────

class TuLanh(BaseModel):
    ma_sp: str
    ten: str
    hang: str
    nguoi_min: float
    nguoi_max: float
    dung_tich_lit: float | None = None
    dung_tich_la_tong: bool = False       # TC-006: phai noi ro khi la dung tich TONG
    dien_kwh_nam: float | None = None
    ngang_cm: float | None = None
    cao_cm: float | None = None
    sau_cm: float | None = None
    kieu_dang: str = ""
    so_cua: str = ""
    inverter: bool = False
    gia: int
    gia_goc: int
    qua: str = ""
    nguon: dict[str, Nguon] = Field(default_factory=dict)


def _ng(truong, gia_tri, ma, tu, suy_luan=False) -> Nguon:
    return Nguon(truong=truong, gia_tri=str(gia_tri), nguon=tu,
                 lay_luc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 ma_sp=ma, suy_luan=suy_luan)


_DS: list[TuLanh] | None = None


def tai_catalog_tu_lanh() -> list[TuLanh]:
    global _DS
    if _DS is not None:
        return _DS
    duong_dan = MAC_DINH if MAC_DINH.exists() else DU_PHONG_MAU
    if not duong_dan.exists():
        _DS = []                          # khong co du lieu -> nganh tat, router se tu choi lich su
        return _DS

    def _f(x):
        try:
            return float(x) if str(x).strip() else None
        except ValueError:
            return None

    ds = []
    with open(duong_dan, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ma = r["ma_sp"]
            dt, kwh = _f(r["dung_tich_lit"]), _f(r["dien_kwh_nam"])
            la_tong = r.get("dung_tich_la_tong") == "1"
            ds.append(TuLanh(
                ma_sp=ma, ten=r["ten"], hang=r["hang"],
                nguoi_min=float(r["nguoi_min"]), nguoi_max=float(r["nguoi_max"]),
                dung_tich_lit=dt, dung_tich_la_tong=la_tong,
                dien_kwh_nam=kwh,
                ngang_cm=_f(r["ngang_cm"]), cao_cm=_f(r["cao_cm"]), sau_cm=_f(r["sau_cm"]),
                kieu_dang=r["kieu_dang"], so_cua=r["so_cua"],
                inverter=r["inverter"] == "1",
                gia=int(r["gia"]), gia_goc=int(r["gia_goc"]),
                qua=(r.get("qua") or "").strip(),
                nguon={
                    "nguoi_phu_hop": _ng("nguoi_phu_hop",
                                         f"{r['nguoi_min']}-{r['nguoi_max']} nguoi",
                                         ma, "catalog:Số người sử dụng"),
                    "gia": _ng("gia", r["gia"], ma, "price_api"),
                    **({"qua": _ng("qua", (r.get("qua") or "").strip(), ma,
                                   "catalog:khuyến mãi quà")}
                       if (r.get("qua") or "").strip() else {}),
                    "gia_goc": _ng("gia_goc", r["gia_goc"], ma, "price_api"),
                    "dung_tich_lit": _ng("dung_tich_lit", dt, ma,
                                         "catalog:Dung tích tổng" if la_tong
                                         else "catalog:Dung tích sử dụng",
                                         suy_luan=la_tong),
                    "dien_kwh_nam": _ng("dien_kwh_nam", kwh, ma, "catalog:Điện năng tiêu thụ"),
                    "ngang_cm": _ng("ngang_cm", _f(r["ngang_cm"]), ma, "catalog:Ngang"),
                    "cao_cm": _ng("cao_cm", _f(r["cao_cm"]), ma, "catalog:Cao"),
                    "sau_cm": _ng("sau_cm", _f(r["sau_cm"]), ma, "catalog:Sâu"),
                },
            ))
    _DS = ds
    return ds


# ── Trich o nhu cau (luat + ngu canh, khong LLM - mau cau tu lanh rat co khuon) ──

_KIEU_DANG = [
    (r"side\s*by\s*side|2 canh doi|tu doi", "Side by Side"),
    (r"multi\s*door|nhieu cua|4 canh", "Multi Door"),
    (r"\bmini\b|tu nho", "Mini"),
    (r"ngan da duoi", "Ngăn đá dưới"),
    (r"ngan da tren", "Ngăn đá trên"),
]


def trich_tu_lanh(text: str, cu: ONhuCauTuLanh | None = None,
                  o_dang_cho: str | None = None) -> ONhuCauTuLanh:
    t = chuan_hoa(text)
    kd = bo_dau(t).lower()
    nc = (cu or ONhuCauTuLanh()).model_copy()

    # so nguoi: "nha 4 nguoi", "gia dinh 5 nguoi"
    m = re.search(r"(?:nha|gia dinh|cho)?\s*(\d{1,2})\s*(?:nguoi|thanh vien)", kd)
    if m and nc.so_nguoi is None:
        nc.so_nguoi = int(m.group(1))

    # ngan sach (chuan_hoa da doi 15tr -> 15000000). So moi GHI DE so cu -
    # khach doi y "thoi 10tr thoi" phai an, khong lang le giu so cu.
    m = re.search(r"(?:duoi|khoang|tam|toi da|max|gia)\s*([\d]{6,})", kd) \
        or re.search(r"\b([\d]{7,})\b", kd)
    if m:
        nc.ngan_sach_max = int(m.group(1))

    # hoc bep: "60x65x86", "hoc 60 x 65 x 86 cm" (Ngang x Sau x Cao theo thoi quen ghi)
    m = re.search(r"(\d{2,3})\s*[x×]\s*(\d{2,3})\s*[x×]\s*(\d{2,3})", kd)
    if m:
        nc.ngang_cm, nc.sau_cm, nc.cao_cm = (float(m.group(i)) for i in (1, 2, 3))
    else:
        m = re.search(r"(?:rong|ngang)\s*(?:chi\s*)?(\d{2,3})\s*cm", kd)
        if m:
            nc.ngang_cm = float(m.group(1))

    for mau, ten in _KIEU_DANG:
        if re.search(mau, kd):
            nc.kieu_dang = ten
            break

    if re.search(r"tiet kiem dien|it ton dien|inverter|tkd", kd) \
            and UuTienTL.TIET_KIEM_DIEN not in nc.uu_tien:
        nc.uu_tien.append(UuTienTL.TIET_KIEM_DIEN)
    if re.search(r"dung tich lon|chua nhieu|rong rai|to\b", kd) \
            and UuTienTL.DUNG_TICH not in nc.uu_tien:
        nc.uu_tien.append(UuTienTL.DUNG_TICH)
    if re.search(r"\bre\b|gia re|khuyen mai|giam gia", kd) \
            and UuTienTL.GIA not in nc.uu_tien:
        nc.uu_tien.append(UuTienTL.GIA)

    # tra loi cut lun theo ngu canh o vua hoi: "4" khi dang hoi so nguoi
    if o_dang_cho == "so_nguoi" and nc.so_nguoi is None:
        if re.fullmatch(r"\d{1,2}", kd.strip()):
            nc.so_nguoi = int(kd.strip())
    return nc


# ── Loc cung + cham diem + top 3 ────────────────────────────────────────────

def xep_hang_tu_lanh(ds: list[TuLanh], nc: ONhuCauTuLanh) -> tuple[BangKetQua, int]:
    """Tra (bang, so_may_thieu_kich_thuoc_bi_bo) - so sau de NOI THAT khi khach
    rang buoc hoc bep ma 2/3 catalog khong co so kich thuoc (TC-002)."""
    thieu_kich_thuoc = 0
    con, bi_loai = [], []
    for s in ds:
        if nc.hang and s.hang.lower() != nc.hang.lower():
            bi_loai.append((s, "hang", f"khác hãng {nc.hang}"))
            continue
        if nc.so_nguoi is not None and not (s.nguoi_min <= nc.so_nguoi <= s.nguoi_max):
            bi_loai.append((s, "so_nguoi",
                            f"hãng công bố cho {s.nguoi_min:.0f}-{s.nguoi_max:.0f} người, "
                            f"không khớp nhà {nc.so_nguoi} người"))
            continue
        if nc.ngan_sach_max and s.gia > nc.ngan_sach_max:
            bi_loai.append((s, "ngan_sach", "vượt ngân sách"))
            continue
        if nc.ngang_cm is not None:
            # TC-002: dung Ngang lam hard filter; thieu so -> KHONG doan
            if s.ngang_cm is None:
                thieu_kich_thuoc += 1
                continue
            if s.ngang_cm > nc.ngang_cm or \
               (nc.cao_cm and s.cao_cm and s.cao_cm > nc.cao_cm) or \
               (nc.sau_cm and s.sau_cm and s.sau_cm > nc.sau_cm):
                bi_loai.append((s, "kich_thuoc", "không vừa hốc bếp"))
                continue
        if nc.kieu_dang and nc.kieu_dang.lower() not in s.kieu_dang.lower():
            bi_loai.append((s, "kieu_dang", f"kiểu dáng {s.kieu_dang}"))
            continue
        con.append(s)

    # trong so: uu tien khach neu + gia luon co mat
    ts: dict[UuTienTL, float] = {u: 0.4 for u in nc.uu_tien}
    ts.setdefault(UuTienTL.GIA, 0.2)
    ts.setdefault(UuTienTL.TIET_KIEM_DIEN, 0.2)      # tu lanh chay 24/7 - dien luon dang quan tam
    tong_ts = sum(ts.values())
    ts = {k: v / tong_ts for k, v in ts.items()}

    TRUC = {
        UuTienTL.TIET_KIEM_DIEN: ("điện năng", lambda s: s.dien_kwh_nam, True,
                                  lambda v: f"{v:.0f} kWh/năm"),
        UuTienTL.DUNG_TICH: ("dung tích", lambda s: s.dung_tich_lit, False,
                             lambda v: f"{v:.0f} lít"),
        UuTienTL.GIA: ("giá", lambda s: float(s.gia), True,
                       lambda v: f"{v/1e6:.2f}".rstrip("0").rstrip(".") + " tr"),
    }

    def _chuan(vals, thap_tot):
        co = [v for v in vals if v is not None]
        if not co or max(co) == min(co):
            return [0.5] * len(vals)
        lo, hi = min(co), max(co)
        return [0.5 if v is None else (1 - (v - lo) / (hi - lo) if thap_tot else (v - lo) / (hi - lo))
                for v in vals]

    diem = [0.0] * len(con)
    for u, w in ts.items():
        _, lay, thap_tot, _ = TRUC[u]
        for i, d in enumerate(_chuan([lay(s) for s in con], thap_tot)):
            diem[i] += w * d
    xep = sorted(zip(con, diem), key=lambda x: -x[1])
    top = [s for s, _ in xep[:3]]

    ung_vien = []
    for s, d in xep[:3]:
        hon, kem = [], []
        for u in ts:
            ten, lay, thap_tot, fmt = TRUC[u]
            v = lay(s)
            doi = [o for o in top if o.ma_sp != s.ma_sp and lay(o) is not None]
            if v is None or not doi:
                continue
            best = (min if thap_tot else max)(doi, key=lay)
            bv = lay(best)
            (hon if ((v < bv) if thap_tot else (v > bv)) else kem if v != bv else []).append(
                TrucSoSanh(truc=ten, cua_minh=fmt(v), doi_thu=f"{best.ten} {fmt(bv)}"))
        ung_vien.append(UngVien(ma_sp=s.ma_sp, ten=s.ten, gia=s.gia, diem=round(d, 4),
                                hon=hon, kem=kem, nguon=list(s.nguon.values())))

    loai_nb = None
    ung = [x for x in bi_loai if x[1] == "so_nguoi"]
    if ung:
        sp, ly_do, chi_tiet = min(ung, key=lambda x: x[0].gia)
        loai_nb = LyDoLoai(ma_sp=sp.ma_sp, ten=sp.ten, ly_do=ly_do, chi_tiet=chi_tiet)

    return BangKetQua(top3=ung_vien, loai_noi_bat=loai_nb,
                      tong_truoc_loc=len(ds), con_lai_sau_loc=len(con)), thieu_kich_thuoc


# ── Serialize cho LLM viet lai (dua vao viet_lai qua mo_ta_nhu_cau) ─────────

def bang_thanh_chu_tu_lanh(bang: BangKetQua, nc: ONhuCauTuLanh,
                           thieu_kich_thuoc: int, giong: str) -> str:
    d = [f"NHU CẦU KHÁCH (TỦ LẠNH): nhà {nc.so_nguoi} người"]
    if nc.hang:
        d.append(f"chỉ xét hãng {nc.hang}")
    if nc.ngan_sach_max and nc.ngan_sach_max >= 10**11:
        d.append("KHÔNG giới hạn ngân sách")
    elif nc.ngan_sach_max:
        d.append(f"ngân sách {nc.ngan_sach_max/1e6:.0f} triệu")
    if nc.ngang_cm:
        d.append(f"hốc bếp ngang {nc.ngang_cm:.0f} cm"
                 + (f", sâu {nc.sau_cm:.0f} cm" if nc.sau_cm else "")
                 + (f", cao {nc.cao_cm:.0f} cm" if nc.cao_cm else ""))
    if nc.kieu_dang:
        d.append(f"kiểu {nc.kieu_dang}")

    ra = [", ".join(d), "",
          f"Đã lọc {bang.tong_truoc_loc} tủ còn {bang.con_lai_sau_loc} phù hợp.", "", "TOP 3:"]
    for i, u in enumerate(bang.top3, 1):
        ra.append(f"{i}. {u.ten} — giá {u.gia:,d}đ".replace(",", "."))
        th = {n.truong: n for n in u.nguon}
        chi_tiet = []
        n_dt = th.get("dung_tich_lit")
        if n_dt and n_dt.gia_tri not in (None, "None"):
            # TC-006: neu chi co dung tich TONG thi phai noi ro, khong duoc
            # trinh bay nhu suc chua thuc te
            nhan = "dung tích TỔNG (hãng không công bố dung tích sử dụng)" \
                if n_dt.suy_luan else "dung tích sử dụng"
            chi_tiet.append(f"{nhan} {float(n_dt.gia_tri):.0f} lít")
        if (n := th.get("dien_kwh_nam")) and n.gia_tri not in (None, "None"):
            chi_tiet.append(f"điện {float(n.gia_tri):.0f} kWh/năm")
        if (n := th.get("nguoi_phu_hop")):
            chi_tiet.append(f"cho {n.gia_tri}")
        if chi_tiet:
            ra.append("   " + " · ".join(chi_tiet))
        for h in u.hon:
            ra.append(dong_so_sanh(h, la_hon=True))
        for k in u.kem:
            ra.append(dong_so_sanh(k, la_hon=False))

    if bang.loai_noi_bat:
        ra += ["", f"KHÔNG ĐỀ XUẤT: {bang.loai_noi_bat.ten} — {bang.loai_noi_bat.chi_tiet}"]
    if thieu_kich_thuoc:
        ra += ["", f"LƯU Ý PHẢI NÓI: {thieu_kich_thuoc} tủ khác không có dữ liệu kích thước "
                   "nên em không xác nhận được có vừa hốc bếp không — em không đoán."]
    return "\n".join(ra)
