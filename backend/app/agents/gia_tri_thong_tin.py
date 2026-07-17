# -*- coding: utf-8 -*-
"""Do GIA TRI THONG TIN - quyet dinh hoi khach cau nao, hoi may cau.

Day la thu tra loi cau hoi ma hau het chatbot tu van bo ngo: khong phai "co nen
hoi khong" ma "hoi CAU NAO". Bat khach dien form 6 o la tra tan; doan bua roi
de xuat lung tung la tu van au.

Cach do: voi moi o con trong, MO PHONG - gia su o do nhan tung gia tri kha di,
chay lai xep hang, xem top 3 lech nhau bao nhieu.
  - Lech nhieu -> cau hoi do dang gia -> hoi.
  - Khong lech -> hoi lam gi cho phien -> bo qua.

Toan bo file KHONG goi LLM. De LLM tu chon cau hoi thi:
  - khong do duoc (khong co diem so nao de giai trinh),
  - khong on dinh (cung dau vao, luot sau hoi khac),
  - va troi flow - LLM quen mat nhu cau ban dau roi hoi lan man.
"""
from __future__ import annotations

from backend.app.ranking.xep_hang import cfg, xep_hang
from backend.app.schemas.ket_qua import CauHoiNguoc
from backend.app.schemas.nhu_cau import GIA_TRI_THU, O_CO_THE_HOI, ONhuCauMayLanh
from backend.app.services.catalog import SanPham


def _khac_tap(a: list[str], b: list[str]) -> float:
    """0 = cung tap san pham, 1 = khong trung con nao."""
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    k = max(len(sa), len(sb)) or 1
    return 1.0 - len(sa & sb) / k


def _khac_thu_tu(a: list[str], b: list[str]) -> float:
    """Kendall tau chuan hoa tren phan CHUNG cua 2 danh sach.

    Tap khac han -> khong so thu tu duoc -> tra 1.0 (lech toi da).
    """
    chung = [x for x in a if x in b]
    if len(chung) < 2:
        return 1.0 if _khac_tap(a, b) > 0 else 0.0
    ia = {x: i for i, x in enumerate(a)}
    ib = {x: i for i, x in enumerate(b)}
    nghich = tong = 0
    for i in range(len(chung)):
        for j in range(i + 1, len(chung)):
            x, y = chung[i], chung[j]
            tong += 1
            if (ia[x] < ia[y]) != (ib[x] < ib[y]):
                nghich += 1
    return nghich / tong if tong else 0.0


def _doi_top1(a: list[str], b: list[str]) -> float:
    """May dung dau co doi khong. 1 = doi, 0 = giu nguyen.

    Tach rieng khoi Kendall tau vi tau tinh moi cap ngang nhau: hoan doi hang
    1<->2 bi cham diem ngang hoan doi 2<->3. Voi khach thi khong ngang: may
    dung dau la may ho se mua.
    """
    if not a or not b:
        return 1.0 if a != b else 0.0
    return 0.0 if a[0] == b[0] else 1.0


def do_lech(a: list[str], b: list[str]) -> float:
    g = cfg()["gia_tri_thong_tin"]
    return (
        g["trong_so_khac_tap"] * _khac_tap(a, b)
        + g["trong_so_khac_thu_tu"] * _khac_thu_tu(a, b)
        + g["trong_so_doi_top1"] * _doi_top1(a, b)
    )


def diem_gia_tri(ten_o: str, ds: list[SanPham], nhu_cau: ONhuCauMayLanh) -> float | None:
    """Dien o nay vao thi top 3 doi bao nhieu? Tra 0..1, None neu khong mo phong duoc."""
    kha_di = GIA_TRI_THU.get(ten_o)
    if not kha_di:
        return None
    tops = [[u.ma_sp for u in xep_hang(ds, nhu_cau.gan(ten_o, v)).top3] for v in kha_di]
    cap = [
        do_lech(tops[i], tops[j]) for i in range(len(tops)) for j in range(i + 1, len(tops))
    ]
    return sum(cap) / len(cap) if cap else 0.0


def bang_diem(ds: list[SanPham], nhu_cau: ONhuCauMayLanh) -> list[tuple[str, float]]:
    """Diem tung o con trong, cao -> thap. Dung de log va giai trinh voi giam khao."""
    out = []
    for o in nhu_cau.con_trong():
        d = diem_gia_tri(o, ds, nhu_cau)
        if d is not None:
            out.append((o, round(d, 4)))
    return sorted(out, key=lambda x: -x[1])


def chon_cau_hoi(ds: list[SanPham], nhu_cau: ONhuCauMayLanh) -> CauHoiNguoc | None:
    """Cau hoi nguoc tiep theo, hoac None neu du de tra loi roi.

    Thu tu uu tien:
      1. Thieu o BAT BUOC -> hoi ngay, khoi do. Khong co ngan sach/dien tich thi
         khong loc cung duoc, mo phong cung vo nghia.
      2. Con lai -> do gia tri thong tin, lay o cao diem nhat NEU vuot nguong.
      3. Duoi nguong het -> None: dung hoi nua, tra loi di.
    """
    cau = cfg()["cau_hoi"]

    thieu = nhu_cau.thieu_bat_buoc()
    if thieu:
        o = thieu[0]
        return CauHoiNguoc(o_hoi=o, cau_hoi=cau[o], diem_gia_tri=1.0)

    diem = bang_diem(ds, nhu_cau)
    if not diem:
        return None
    o, d = diem[0]
    if d < cfg()["gia_tri_thong_tin"]["nguong_hoi"]:
        return None
    return CauHoiNguoc(o_hoi=o, cau_hoi=cau[o], diem_gia_tri=d)
