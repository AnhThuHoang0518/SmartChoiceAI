# -*- coding: utf-8 -*-
"""Adapter catalog - doc san pham da chuan hoa tu data/processed/.

Tang nay KHONG dung toi file goc NDA. `scripts/nap_dmx.py` lo viec do. Nho vay
khi doi tac cap API that thi chi thay tang nap, khong dung vao logic tu van.

Moi truong deu keo theo Nguon -> hau kiem doi chieu nguoc duoc, UI gan badge
bam ra nguon duoc. Khong co truong nao "tran" khong nguon.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from backend.app.schemas.ket_qua import Nguon

MAC_DINH = Path("data/processed/may_lanh.csv")

# Du lieu THAT (NDA, khong co tren repo) vang -> tu roi ve catalog MAU gia lap.
# Nho vay nguoi cham clone repo ve la chay duoc ngay, khong can xin file NDA.
# Thu tu uu tien: that -> mau. Xem scripts/sinh_catalog_mau.py.
DU_PHONG_MAU = Path("data/mock/catalog/may_lanh_mau.csv")


def _bay_gio() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _so(x) -> float | None:
    s = str(x or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


class SanPham(BaseModel):
    ma_sp: str
    ten: str
    hang: str
    pham_vi_min: float
    pham_vi_max: float
    gia: int
    gia_goc: int
    do_on_db: float | None = None
    cspf: float | None = Field(None, description="Hieu suat nang luong - CAO hon la tot dien hon")
    sao: float | None = None
    inverter: bool = False
    lam_lanh_nhanh: bool = False
    loai_may: str = ""
    nguon: dict[str, Nguon] = Field(default_factory=dict)

    def phu_duoc(self, m2: float) -> bool:
        """Hang co cong bo may nay dung cho phong m2 nay khong.

        Chat: phai nam TRONG khoang hang cong bo, khong phai 'cang manh cang tot'.
        May qua du cong suat thi khach mua dat hon va may chay ngat quang (short
        cycle) - hut am kem, mau hong. Hang biet dieu do nen moi ghi khoang.
        """
        return self.pham_vi_min <= m2 <= self.pham_vi_max

    def co_khuyen_mai(self) -> bool:
        return self.gia < self.gia_goc

    def nguon_cua(self, truong: str) -> Nguon | None:
        return self.nguon.get(truong)


def _nguon(truong: str, gia_tri, ma_sp: str, tu: str, suy_luan: bool = False) -> Nguon:
    return Nguon(
        truong=truong,
        gia_tri=str(gia_tri),
        nguon=tu,
        lay_luc=_bay_gio(),
        ma_sp=ma_sp,
        suy_luan=suy_luan,
    )


def tai_catalog(duong_dan: str | Path | None = None) -> list[SanPham]:
    # None (mac dinh) -> uu tien du lieu THAT, vang thi roi ve MAU gia lap.
    # Dung sentinel None thay vi default=MAC_DINH: default arg bind luc def,
    # doi bien module sau do khong an - loi da dinh mot lan khi test fallback.
    if duong_dan is None:
        if MAC_DINH.exists():
            duong_dan = MAC_DINH
        elif DU_PHONG_MAU.exists():
            duong_dan = DU_PHONG_MAU
        else:
            raise FileNotFoundError(
                f"Khong co du lieu: thieu ca {MAC_DINH} (du lieu that, sinh bang "
                f"scripts/nap_dmx.py) lan {DU_PHONG_MAU} (mau, sinh bang "
                f"scripts/sinh_catalog_mau.py)."
            )
    duong_dan = Path(duong_dan)

    ds: list[SanPham] = []
    with open(duong_dan, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ma = r["ma_sp"]
            do_on, cspf, sao = _so(r["do_on_db"]), _so(r["cspf"]), _so(r["sao"])
            gia, gia_goc = int(r["gia"]), int(r["gia_goc"])
            ds.append(
                SanPham(
                    ma_sp=ma,
                    ten=r["ten"],
                    hang=r["hang"],
                    pham_vi_min=float(r["pham_vi_min"]),
                    pham_vi_max=float(r["pham_vi_max"]),
                    gia=gia,
                    gia_goc=gia_goc,
                    do_on_db=do_on,
                    cspf=cspf,
                    sao=sao,
                    inverter=r["inverter"] == "1",
                    lam_lanh_nhanh=r["lam_lanh_nhanh"] == "1",
                    loai_may=r["loai_may"],
                    nguon={
                        "pham_vi": _nguon(
                            "pham_vi",
                            f"{r['pham_vi_min']}-{r['pham_vi_max']}m²",
                            ma,
                            "catalog:Phạm vi sử dụng",
                        ),
                        "gia": _nguon("gia", gia, ma, "price_api"),
                        "do_on_db": _nguon("do_on_db", do_on, ma, "catalog:Độ ồn"),
                        "cspf": _nguon("cspf", cspf, ma, "catalog:Nhãn năng lượng"),
                        "inverter": _nguon("inverter", r["inverter"], ma, "catalog:Loại Inverter"),
                        # 2 truong duoi phuc vu GIONG KY THUAT (khach ranh thong so
                        # duoc xem day du) - phai co nguon thi hau kiem moi cho noi.
                        "sao": _nguon("sao", sao, ma, "catalog:Nhãn năng lượng"),
                        "gia_goc": _nguon("gia_goc", gia_goc, ma, "price_api"),
                    },
                )
            )
    return ds
