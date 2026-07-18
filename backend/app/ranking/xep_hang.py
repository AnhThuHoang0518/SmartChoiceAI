# -*- coding: utf-8 -*-
"""Lop quyet dinh - loc cung, cham diem, top 3, trade-off.

TOAN BO file nay KHONG goi LLM. Day la chu y kien truc, khong phai tiet kiem:
  - LLM khong tinh duoc so on dinh -> de bia gia/thong so.
  - LLM khong giai trinh duoc vi sao xep A tren B -> mat diem "giai thich trade-off".
  - LLM cham (0.8-2s/luot) -> vo moc <5s cua de bai.
LLM chi duoc dien dat KET QUA cua file nay, o buoc sau.
"""
from __future__ import annotations

import json
from pathlib import Path

from backend.app.schemas.ket_qua import BangKetQua, LyDoLoai, TrucSoSanh, UngVien
from backend.app.schemas.nhu_cau import LoaiPhong, ONhuCauMayLanh, UuTien
from backend.app.services.catalog import SanPham

_CFG: dict | None = None


def cfg(duong_dan: str | Path = "configs/may_lanh.json") -> dict:
    global _CFG
    if _CFG is None:
        _CFG = json.loads(Path(duong_dan).read_text(encoding="utf-8"))
    return _CFG


# ── Tai nhiet ───────────────────────────────────────────────────────────────

def dien_tich_hieu_dung(dien_tich_m2: float, co_nang: bool | None) -> float:
    """Dien tich QUY DOI theo tai nhiet, de doi chieu voi pham vi hang cong bo.

    Khong con bang tra m2->HP: du lieu that co 'Cong suat dau ra' trong 82%,
    nhung 'Pham vi su dung' phu 91% - chinh hang da ghi may nay cho phong bao
    nhieu m2. Dung thang, khoi suy dien.

    co_nang=None (chua hoi) -> tinh nhu khong nang. Day la ly do 'co_nang' luon
    la o dang hoi nhat: no doi han danh sach may phu hop.
    """
    return dien_tich_m2 * (cfg()["tai_nhiet"]["he_so_nang"] if co_nang else 1.0)


# ── Truc cham diem ──────────────────────────────────────────────────────────
# (ten hien thi, lay gia tri, cang_thap_cang_tot, dinh dang)

def _fmt_tien(v) -> str:
    return f"{v / 1_000_000:.2f}".rstrip("0").rstrip(".") + " tr"


# Truc cham diem, chon theo DU LIEU THAT co gi dung duoc:
#   - tiet kiem dien -> CSPF (nhan nang luong). Cot 'Dien nang tieu thu' cua file
#     that chi co '0','1','2' -> rac, khong dung. CSPF cao = tot dien hon.
#   - do on -> min dan lanh (che do quat em nhat).
#   - lam lanh nhanh -> co Turbo/Powerful/Jet Cool khong (cot 'Cong nghe lam lanh').
#   - do ben: KHONG co truc. File that khong co truong nao do duoc do ben mot
#     cach trung thuc -> tha bo con hon cham bua roi giai thich lao.
TRUC = {
    UuTien.TIET_KIEM_DIEN: ("tiết kiệm điện", lambda s: s.cspf, False, lambda v: f"CSPF {v}"),
    UuTien.DO_ON: ("độ ồn", lambda s: s.do_on_db, True, lambda v: f"{v:.0f} dB"),
    UuTien.LAM_LANH_NHANH: ("làm lạnh nhanh", lambda s: float(s.lam_lanh_nhanh), False,
                            lambda v: "có Turbo" if v else "không Turbo"),
    UuTien.GIA: ("giá", lambda s: float(s.gia), True, _fmt_tien),
}


def trong_so(nhu_cau: ONhuCauMayLanh) -> dict[UuTien, float]:
    """Trong so sinh tu CHINH loi khach noi, khong phai hang so ai do dat san.

    'gia' luon co mat du khach khong nhac - khong ai khong quan tam gia.
    Do on duoc nhan them neu la phong ngu (nam ngu nghe tieng may la hong).
    """
    c = cfg()["cham_diem"]
    ts: dict[UuTien, float] = {}
    for u in nhu_cau.uu_tien:
        if u in TRUC:
            ts[u] = c["trong_so_uu_tien"]
    ts.setdefault(UuTien.GIA, c["trong_so_gia_mac_dinh"])

    if UuTien.DO_ON in ts and nhu_cau.loai_phong is not None:
        nhan = (
            c["nhan_do_on_phong_ngu"]
            if nhu_cau.loai_phong == LoaiPhong.NGU
            else c["nhan_do_on_phong_khach"]
        )
        ts[UuTien.DO_ON] *= nhan

    tong = sum(ts.values()) or 1.0
    return {k: v / tong for k, v in ts.items()}


# ── Loc cung ────────────────────────────────────────────────────────────────

def loc_cung(
    ds: list[SanPham], nhu_cau: ONhuCauMayLanh
) -> tuple[list[SanPham], list[tuple[SanPham, str, str]]]:
    """Loai thang tay theo rang buoc CUNG. Tra (con lai, danh sach bi loai + ly do).

    Ghi lai ly do loai de sau con chu dong noi voi khach 'vi sao khong de xuat
    con may anh/chi dang nham' - day la thu an diem trade-off.
    """
    m2 = (
        dien_tich_hieu_dung(nhu_cau.dien_tich_m2, nhu_cau.co_nang)
        if nhu_cau.dien_tich_m2
        else None
    )
    con_lai, bi_loai = [], []
    for s in ds:
        h = getattr(nhu_cau, "hang", None)
        if h and s.hang.lower() != h.lower():
            bi_loai.append((s, "hang", f"khác hãng {h}"))
            continue
        ht = getattr(nhu_cau, "hang_tru", None)
        if ht and s.hang.lower() == ht.lower():
            bi_loai.append((s, "hang", f"khách không muốn hãng {ht}"))
            continue
        ci = getattr(nhu_cau, "can_inverter", None)
        if ci is not None and s.inverter != ci:
            bi_loai.append((s, "inverter",
                            "máy mono (khách cần Inverter)" if ci else "máy Inverter (khách cần mono)"))
            continue
        if m2 is not None and not s.phu_duoc(m2):
            do = "không đủ tải" if s.pham_vi_max < m2 else "dư công suất, chạy ngắt quãng"
            bi_loai.append(
                (s, "pham_vi",
                 f"hãng công bố cho phòng {s.pham_vi_min:.0f}-{s.pham_vi_max:.0f}m², "
                 f"{do} với phòng {nhu_cau.dien_tich_m2:.0f}m²"
                 + (" có nắng" if nhu_cau.co_nang else ""))
            )
            continue
        if nhu_cau.ngan_sach_max and s.gia > nhu_cau.ngan_sach_max:
            bi_loai.append((s, "ngan_sach", f"{_fmt_tien(s.gia)} vượt ngân sách "
                                            f"{_fmt_tien(nhu_cau.ngan_sach_max)}"))
            continue
        con_lai.append(s)
    return con_lai, bi_loai


# ── Cham diem ───────────────────────────────────────────────────────────────

def _chuan_hoa(gia_tri: list[float | None], thap_tot: bool) -> list[float]:
    """Min-max ve 0-1 trong CHINH tap ung vien con lai.

    Thieu du lieu -> 0.5 trung tinh, khong thuong khong phat. Cho 0 la vu oan
    san pham chi vi catalog thieu field.
    """
    co = [v for v in gia_tri if v is not None]
    if not co:
        return [0.5] * len(gia_tri)
    lo, hi = min(co), max(co)
    if hi == lo:
        return [0.5 if v is None else 1.0 for v in gia_tri]
    out = []
    for v in gia_tri:
        if v is None:
            out.append(0.5)
        else:
            t = (v - lo) / (hi - lo)
            out.append(1.0 - t if thap_tot else t)
    return out


def cham_diem(ds: list[SanPham], nhu_cau: ONhuCauMayLanh) -> list[tuple[SanPham, float]]:
    ts = trong_so(nhu_cau)
    if not ds:
        return []
    diem = [0.0] * len(ds)
    for u, w in ts.items():
        _, lay, thap_tot, _ = TRUC[u]
        for i, d in enumerate(_chuan_hoa([lay(s) for s in ds], thap_tot)):
            diem[i] += w * d
    return sorted(zip(ds, diem), key=lambda x: -x[1])


# ── Trade-off ───────────────────────────────────────────────────────────────

def _trade_off(sp: SanPham, doi_thu: list[SanPham], nhu_cau: ONhuCauMayLanh):
    """So sp voi doi thu manh nhat TUNG TRUC -> duoc gi / mat gi.

    Code sinh ra bang nay. LLM KHONG duoc tu nghi ra cai nao hon cai nao.
    """
    hon, kem = [], []
    for u in trong_so(nhu_cau):
        ten, lay, thap_tot, fmt = TRUC[u]
        v = lay(sp)
        if v is None:
            continue
        ung = [o for o in doi_thu if lay(o) is not None]
        if not ung:
            continue
        best = (min if thap_tot else max)(ung, key=lay)
        bv = lay(best)
        tot_hon = (v < bv) if thap_tot else (v > bv)
        if tot_hon:
            hon.append(TrucSoSanh(truc=ten, cua_minh=fmt(v), doi_thu=f"{best.ten} {fmt(bv)}"))
        elif v != bv:
            kem.append(TrucSoSanh(truc=ten, cua_minh=fmt(v), doi_thu=f"{best.ten} {fmt(bv)}"))
    return hon, kem


def _loai_noi_bat(bi_loai: list[tuple[SanPham, str, str]]) -> LyDoLoai | None:
    """Chon may bi loai DANG noi nhat de chu dong giai thich voi khach.

    Khong phai may re nhat: phong 18m2 thi khong ai dang nham may 1HP ca, noi
    ra chi to vo duyen. May khach THUC SU dang nham la bac NGAY DUOI nguong
    (vd can 2.0HP thi khach dang xem 1.5HP vi thay quang cao gia tot) -> loc
    theo bac cao nhat trong so bi loai, roi trong bac do lay may re nhat.
    """
    ung = [x for x in bi_loai if x[1] == "pham_vi" and "không đủ tải" in x[2]]
    if not ung:
        return None
    bac_gan_nhat = max(x[0].pham_vi_max for x in ung)
    gan = [x for x in ung if x[0].pham_vi_max == bac_gan_nhat]
    sp, ly_do, chi_tiet = min(gan, key=lambda x: x[0].gia)
    return LyDoLoai(ma_sp=sp.ma_sp, ten=sp.ten, ly_do=ly_do, chi_tiet=chi_tiet)


# ── Ham chinh ───────────────────────────────────────────────────────────────

def xep_hang(ds: list[SanPham], nhu_cau: ONhuCauMayLanh, lay_top: int = 3) -> BangKetQua:
    con_lai, bi_loai = loc_cung(ds, nhu_cau)
    xep = cham_diem(con_lai, nhu_cau)
    top = [sp for sp, _ in xep[:lay_top]]

    ung_vien = []
    for sp, diem in xep[:lay_top]:
        hon, kem = _trade_off(sp, [o for o in top if o.ma_sp != sp.ma_sp], nhu_cau)
        ung_vien.append(
            UngVien(
                ma_sp=sp.ma_sp,
                ten=sp.ten,
                gia=sp.gia,
                diem=round(diem, 4),
                hon=hon,
                kem=kem,
                nguon=list(sp.nguon.values()),
            )
        )

    return BangKetQua(
        top3=ung_vien,
        loai_noi_bat=_loai_noi_bat(bi_loai),
        dien_tich_hieu_dung_m2=(
            round(dien_tich_hieu_dung(nhu_cau.dien_tich_m2, nhu_cau.co_nang), 1)
            if nhu_cau.dien_tich_m2
            else None
        ),
        tong_truoc_loc=len(ds),
        con_lai_sau_loc=len(con_lai),
    )
