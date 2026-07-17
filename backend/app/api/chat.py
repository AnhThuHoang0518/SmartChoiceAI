# -*- coding: utf-8 -*-
"""Endpoint /chat - rap toan bo luong lai.

Thu tu o day CHINH LA so do kien truc, doc tu tren xuong:
    chuan hoa TV -> trich o nhu cau (LLM #1) -> may trang thai
      -> du o chua?
          CHUA: do gia tri thong tin -> 1 cau hoi template  (KHONG qua LLM)
          RUI : loc cung -> cham diem -> top 3 + trade-off  (KHONG qua LLM)
                -> viet lai (LLM #2) -> hau kiem -> tra khach

Dung 2 lan cham LLM cho ca luot. Moi thu quyet dinh deu la code.
"""
from __future__ import annotations

import time

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.agents.gia_tri_thong_tin import bang_diem, chon_cau_hoi
from backend.app.agents.trich_o_nhu_cau import trich
from backend.app.agents.viet_lai import viet_lai
from backend.app.core import phien
from backend.app.ranking.xep_hang import xep_hang
from backend.app.services.catalog import tai_catalog
from backend.app.services.llm import tao_llm

router = APIRouter()

_DS = None
_LLM = None


def catalog():
    global _DS
    if _DS is None:
        _DS = tai_catalog()
    return _DS


def llm():
    global _LLM
    if _LLM is None:
        _LLM = tao_llm()
    return _LLM


class TinNhan(BaseModel):
    tin_nhan: str
    phien_id: str | None = None


class TraLoi(BaseModel):
    phien_id: str
    loai: str = Field(description="'cau_hoi' = đang hỏi ngược | 'tu_van' = đã ra top 3")
    text: str
    o_nhu_cau: dict = Field(default_factory=dict)
    # Minh bach: tra ra ca bang diem gia tri thong tin de giai trinh VI SAO hoi
    # cau nay ma khong hoi cau kia. Giam khao bam vao xem duoc.
    vi_sao_hoi: list[dict] = Field(default_factory=list)
    top3: list[dict] = Field(default_factory=list)
    loai_noi_bat: dict | None = None
    thong_ke: dict = Field(default_factory=dict)


@router.post("/chat", response_model=TraLoi)
def chat(t: TinNhan) -> TraLoi:
    t0 = time.perf_counter()
    ma = t.phien_id if t.phien_id and phien.lay(t.phien_id) else phien.tao_phien()
    p = phien.lay(ma)

    ds = catalog()
    nc = trich(t.tin_nhan, llm(), p["nhu_cau"])

    diem = [{"o": o, "diem": d} for o, d in bang_diem(ds, nc)]
    hoi = chon_cau_hoi(ds, nc)

    if hoi:
        phien.ghi(ma, nc, hoi.o_hoi)
        return TraLoi(
            phien_id=ma,
            loai="cau_hoi",
            text=hoi.cau_hoi,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            vi_sao_hoi=diem,
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1},
        )

    phien.ghi(ma, nc)
    bang = xep_hang(ds, nc)
    r = viet_lai(bang, nc, llm())

    return TraLoi(
        phien_id=ma,
        loai="tu_van",
        text=r["text"],
        o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
        vi_sao_hoi=diem,
        top3=[u.model_dump(mode="json") for u in bang.top3],
        loai_noi_bat=bang.loai_noi_bat.model_dump(mode="json") if bang.loai_noi_bat else None,
        thong_ke={
            "ms": int((time.perf_counter() - t0) * 1000),
            "cham_llm": 2,
            "truoc_loc": bang.tong_truoc_loc,
            "sau_loc": bang.con_lai_sau_loc,
            "nguon_llm": r["nguon_llm"],
            "so_lan_chan_bia": r["so_lan_bi_chan"],
            "loi_da_chan": r["loi_da_chan"],
        },
    )
