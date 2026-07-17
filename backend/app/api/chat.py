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
from backend.app.core.chuan_hoa_tv import (
    bo_ngan_sach,
    cau_hoi_cong_suat,
    co_nganh_may_lanh,
    co_nganh_tu_lanh,
    hoi_chu_quan,
    hoi_khuyen_mai,
    hoi_ton_kho,
    nganh_ngoai_pham_vi,
    tu_ky_thuat_trong,
    yeu_cau_thong_so,
)
from backend.app.schemas.nhu_cau import UuTien

# Sentinel "khong gioi han ngan sach": khach noi 'bao nhieu cung duoc' thi day
# van la MOT cau tra loi cho o ngan sach (o bat buoc) - khong the de None vi se
# bi hoi lai. Moi cho hien thi phai doi thanh chu 'khong gioi han'.
KHONG_GIOI_HAN = 10**12
from backend.app.ranking.xep_hang import cfg, xep_hang
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


def _xu_ly_tu_lanh(t: TinNhan, ma: str, p: dict, t0: float, giong: str) -> TraLoi:
    """Luong tu van TU LANH - cung khung sale nhu may lanh: gom o bat buoc ->
    loc cung theo cong bo cua hang -> top 3 + trade-off -> LLM dien dat ->
    hau kiem (ro don vi lit/kwh/cm/nguoi da co san trong guardrail chung).
    """
    import json as _json
    from pathlib import Path as _Path

    from backend.app.agents.viet_lai import viet_lai
    from backend.app.nganh.tu_lanh import (
        bang_thanh_chu_tu_lanh,
        tai_catalog_tu_lanh,
        trich_tu_lanh,
        xep_hang_tu_lanh,
    )

    cfg_tl = _json.loads(_Path("configs/tu_lanh.json").read_text(encoding="utf-8"))
    ds = tai_catalog_tu_lanh()
    if not ds:
        # Chua co du lieu nganh nay tren may dang chay -> noi that.
        return TraLoi(phien_id=ma, loai="ngoai_pham_vi",
                      text="Dạ dữ liệu tủ lạnh chưa được nạp trên hệ thống này ạ — "
                           "mình cần máy lạnh thì em tư vấn được ngay ạ!",
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0})

    p["nganh"] = "tu_lanh"
    o_cho = p["da_hoi"][-1] if p["da_hoi"] else None
    nc = trich_tu_lanh(t.tin_nhan, p.get("nhu_cau_tl"), o_cho)
    if bo_ngan_sach(t.tin_nhan):
        nc = nc.model_copy(update={"ngan_sach_max": KHONG_GIOI_HAN})
    p["nhu_cau_tl"] = nc
    p["luc"] = time.time()

    thieu = nc.thieu_bat_buoc()
    if thieu:
        o = thieu[0]
        text = cfg_tl["cau_hoi_lap_lai" if o in p["da_hoi"] else "cau_hoi"][o]
        p["da_hoi"].append(o)
        return TraLoi(phien_id=ma, loai="cau_hoi", text=text,
                      o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                                "cham_llm": 0, "giong": giong, "nganh": "tu_lanh"})

    bang, thieu_kt = xep_hang_tu_lanh(ds, nc)
    if not bang.top3:
        p["loai_truoc"] = "khong_co_may"
        return TraLoi(phien_id=ma, loai="khong_co_may", text=cfg_tl["khong_co_may"]["mau"],
                      o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                                "cham_llm": 0, "nganh": "tu_lanh"})

    mo_ta = bang_thanh_chu_tu_lanh(bang, nc, thieu_kt, giong)
    r = viet_lai(bang, nc, llm(), giong, mo_ta_nhu_cau=mo_ta)
    p["loai_truoc"] = "tu_van"
    return TraLoi(
        phien_id=ma, loai="tu_van", text=r["text"],
        o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
        top3=[u.model_dump(mode="json") for u in bang.top3],
        loai_noi_bat=bang.loai_noi_bat.model_dump(mode="json") if bang.loai_noi_bat else None,
        thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 2,
                  "truoc_loc": bang.tong_truoc_loc, "sau_loc": bang.con_lai_sau_loc,
                  "nguon_llm": r["nguon_llm"], "so_lan_chan_bia": r["so_lan_bi_chan"],
                  "loi_da_chan": r["loi_da_chan"], "giong": giong, "nganh": "tu_lanh"},
    )


@router.post("/chat", response_model=TraLoi)
def chat(t: TinNhan) -> TraLoi:
    t0 = time.perf_counter()
    ma = t.phien_id if t.phien_id and phien.lay(t.phien_id) else phien.tao_phien()
    p = phien.lay(ma)

    # Khach hoi nganh khac (tu lanh, may giat...) -> noi that pham vi, dung lai
    # cau hoi ngan sach nhu robot hong. Phat hien tu demo that.
    nganh = nganh_ngoai_pham_vi(t.tin_nhan)
    if nganh:
        return TraLoi(
            phien_id=ma,
            loai="ngoai_pham_vi",
            text=cfg()["ngoai_pham_vi"]["mau"].format(nganh=nganh),
            o_nhu_cau=p["nhu_cau"].model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0},
        )

    ds = catalog()
    o_dang_cho = p["da_hoi"][-1] if p["da_hoi"] else None
    nc = trich(t.tin_nhan, llm(), p["nhu_cau"], o_dang_cho)

    # Khach tuyen bo bo ngan sach ("khong quan tam tien nua") -> ghi nhan la
    # KHONG GIOI HAN. Bug demo that: truoc day cau nay bi bo qua, bot lai
    # nguyen van "trong tam 20 trieu em chua tim duoc..." nhu chua nghe thay.
    if bo_ngan_sach(t.tin_nhan):
        nc = nc.model_copy(update={"ngan_sach_max": KHONG_GIOI_HAN})

    # Hoi ton kho/con hang -> noi thang du lieu KHONG co truong ton kho, can
    # Stock API (TC-008/TC-017). Chi tra loi rieng khi cau hoi thuan tuy ve
    # ton kho; hoi kem nhu cau thi flow thuong chay va ghi chu duoc them sau.
    if hoi_ton_kho(t.tin_nhan) and nc.dien_tich_m2 is None:
        phien.ghi(ma, nc, "dien_tich_m2")
        return TraLoi(
            phien_id=ma, loai="thieu_du_lieu",
            text=cfg()["thieu_ton_kho"]["mau"],
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1,
                      "giong": p.get("giong") or "binh_dan"},
        )

    # Tieu chi chu quan (dep/sang) hoac khong co truong do (ben) -> noi that,
    # khong xep hang bua (TC-009/TC-025).
    tieu_chi_cq = hoi_chu_quan(t.tin_nhan)
    if tieu_chi_cq:
        phien.ghi(ma, nc, None)
        return TraLoi(
            phien_id=ma, loai="chu_quan",
            text=cfg()["chu_quan"]["mau"].format(tieu_chi=tieu_chi_cq),
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1,
                      "giong": p.get("giong") or "binh_dan"},
        )

    # ── Giong tu van: binh dan (mac dinh) / ky thuat ────────────────────────
    # Sale that doi giong theo khach. Nhan biet qua chinh ngon ngu khach go:
    # >=2 thuat ngu ky thuat (cong don ca phien) hoac khach chu dong doi
    # "cho xin thong so chi tiet" -> ky thuat, sticky den het phien.
    p["tu_kt"] = set(p.get("tu_kt") or set()) | tu_ky_thuat_trong(t.tin_nhan)
    if yeu_cau_thong_so(t.tin_nhan) or len(p["tu_kt"]) >= 2:
        p["giong"] = "ky_thuat"
    giong = p.get("giong") or "binh_dan"

    # ── ROUTER NGANH: tu lanh co vertical rieng ─────────────────────────────
    # May lanh thang khi khach nhac CA HAI ("mua may lanh va tu lanh") - giu
    # hanh vi cu: tu van nganh chinh truoc, nganh kia nhac trong cau tra loi.
    if (co_nganh_tu_lanh(t.tin_nhan) and not co_nganh_may_lanh(t.tin_nhan)) \
            or p.get("nganh") == "tu_lanh":
        if co_nganh_may_lanh(t.tin_nhan):
            p["nganh"] = "may_lanh"          # khach doi sang may lanh giua chung
        else:
            return _xu_ly_tu_lanh(t, ma, p, t0, giong)

    # ── Nganh hang: slot so 0 cua sale ──────────────────────────────────────
    # Khach da nhac may lanh -> chot nganh. Chua biet nganh + cau mo man khong
    # co thong tin gi -> CHAO va hoi quan tam san pham nao (sale khong tu van
    # thu khach chua chon). Nhung khach da cho dien tich/ngan sach thi khong
    # bat chao lai - hoi thu khach vua ngu y la cung nhac.
    if co_nganh_may_lanh(t.tin_nhan) or cau_hoi_cong_suat(t.tin_nhan):
        p["nganh"] = "may_lanh"
    if p.get("nganh") is None and not nc.model_dump(exclude_none=True, exclude={"uu_tien"}) \
            and not nc.uu_tien:
        da_chao = "nganh" in p["da_hoi"]
        phien.ghi(ma, nc, "nganh")
        mau = cfg()["chao_hoi"]["mau_lap_lai" if da_chao else "mau"]
        return TraLoi(
            phien_id=ma,
            loai="cau_hoi",
            text=mau,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1,
                      "giong": giong},
        )
    if p.get("nganh") is None:
        p["nganh"] = "may_lanh"      # co thong tin phong/tien -> nganh dang bat duy nhat

    # Che do GIAI THICH: khach hoi kien thuc ("cong suat bao nhieu?") chu khong
    # phai nho chon may. Truoc day bi tra loi bang nguyen van cau tu van cu -
    # phat hien tu demo that. Template cung + van trich duoc thong tin trong
    # cau hoi (vd "phong 40m2 can bao nhieu HP" -> dien luon dien tich).
    # Khach hoi khuyen mai -> tra loi bang KHUYEN MAI THAT (gia goc vs gia KM
    # trong catalog), khong phai "hot"/"noi bat" tu phong. Code chon + tinh,
    # khong qua LLM. Sau do van keo ve nhu cau (sale that cung dan tu khuyen
    # mai ve "phong minh bao nhieu m2").
    if hoi_khuyen_mai(t.tin_nhan):
        if UuTien.GIA not in nc.uu_tien:
            nc.uu_tien.append(UuTien.GIA)   # khach quan tam gia -> vao nhu cau
        p["nganh"] = p.get("nganh") or "may_lanh"

    # Chi tra BANG khuyen mai khi CHUA biet phong - biet roi thi di thang vao
    # tu van (trong so gia da duoc nang), dung bat khach tra loi lai dien tich.
    if hoi_khuyen_mai(t.tin_nhan) and nc.dien_tich_m2 is None:
        giam = sorted(
            (s for s in ds if s.gia < s.gia_goc),
            key=lambda s: s.gia_goc - s.gia,
            reverse=True,
        )[:3]
        if giam:
            dong = []
            for s in giam:
                muc = s.gia_goc - s.gia
                dong.append(
                    f"• {s.ten}: {s.gia_goc:,.0f}đ còn {s.gia:,.0f}đ (giảm {muc/1_000_000:.1f} triệu)".replace(",", ".")
                )
            text = (
                "Dạ đang có mấy máy giảm sâu nhất nè ạ:\n" + "\n".join(dong)
                + "\nMáy phù hợp hay không còn tùy phòng mình ạ — phòng mình rộng khoảng bao nhiêu m² để em xem máy nào đang giảm mà VỪA phòng mình ạ?"
            )
        else:
            text = "Dạ hiện tại em chưa thấy máy nào đang có giá khuyến mãi trong dữ liệu ạ. Mình cho em xin diện tích phòng và ngân sách, em lọc máy giá tốt nhất cho mình nhé ạ?"
        phien.ghi(ma, nc, "dien_tich_m2")
        return TraLoi(
            phien_id=ma,
            loai="khuyen_mai",
            text=text,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1,
                      "giong": giong},
        )

    if cau_hoi_cong_suat(t.tin_nhan):
        g = cfg()["giai_thich_cong_suat"]
        if nc.dien_tich_m2:
            # Khach da cho dien tich ("phong 40m2 can bao nhieu HP") -> tra loi
            # thang con so uoc, dung hoi lai thu khach vua noi.
            from backend.app.ranking.xep_hang import dien_tich_hieu_dung

            m2 = dien_tich_hieu_dung(nc.dien_tich_m2, nc.co_nang)
            hp = next(b["hp"] for b in g["bang_uoc_hp"] if m2 <= b["m2_max"])
            text = g["mau_da_biet_dien_tich"].format(
                dien_tich=f"{nc.dien_tich_m2:g}",
                nang_chu=" có nắng" if nc.co_nang else "",
                hp=f"{hp:g}",
            )
            o_cho = "ngan_sach_max" if nc.ngan_sach_max is None else None
        else:
            text = g["mau"]
            o_cho = "dien_tich_m2"
        phien.ghi(ma, nc, o_cho)
        return TraLoi(
            phien_id=ma,
            loai="giai_thich",
            text=text,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1},
        )

    diem = [{"o": o, "diem": d} for o, d in bang_diem(ds, nc)]
    hoi = chon_cau_hoi(ds, nc)

    if hoi:
        # Hoi lai o DA hoi roi -> doi loi + kem vi du, khong lap nguyen van.
        text = (
            cfg()["cau_hoi_lap_lai"].get(hoi.o_hoi, hoi.cau_hoi)
            if hoi.o_hoi in p["da_hoi"]
            else hoi.cau_hoi
        )
        phien.ghi(ma, nc, hoi.o_hoi)
        return TraLoi(
            phien_id=ma,
            loai="cau_hoi",
            text=text,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            # Dang thieu o BAT BUOC thi bang diem gia tri thong tin chua co
            # nghia (chua loc duoc gi) - hien toan 0.00 chi gay roi.
            vi_sao_hoi=[] if nc.thieu_bat_buoc() else diem,
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1},
        )

    phien.ghi(ma, nc)
    bang = xep_hang(ds, nc)

    if not bang.top3:
        # Loc xong 0 may. Tim gia thap nhat cua may DU TAI (bo qua ngan sach)
        # de goi huong that cho khach thay vi cau xin loi suong.
        from backend.app.ranking.xep_hang import loc_cung

        nc_khong_ngan_sach = nc.model_copy(update={"ngan_sach_max": None})
        du_tai, _ = loc_cung(ds, nc_khong_ngan_sach)
        gia_min = min((s.gia for s in du_tai), default=None)
        if p.get("loai_truoc") == "khong_co_may":
            # Lan thu 2 lien tiep khong co may -> DOI LOI, huong dan cu the
            # khach phai noi gi. Lap nguyen van la robot hong (bug demo that).
            text = cfg()["khong_co_may"]["mau_lap_lai"]
        else:
            ns = nc.ngan_sach_max
            text = cfg()["khong_co_may"]["mau"].format(
                ngan_sach=("không giới hạn" if ns and ns >= 10**11
                           else f"{ns/1_000_000:.0f} triệu" if ns else "này"),
                dien_tich=(f"{nc.dien_tich_m2:.0f}" if nc.dien_tich_m2 else "?"),
                gia_thap_nhat=(f"{gia_min/1_000_000:.1f} triệu" if gia_min else "cao hơn"),
            )
        p["loai_truoc"] = "khong_co_may"
        return TraLoi(
            phien_id=ma,
            loai="khong_co_may",
            text=text,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            thong_ke={
                "ms": int((time.perf_counter() - t0) * 1000),
                "cham_llm": 1,
                "truoc_loc": bang.tong_truoc_loc,
                "sau_loc": 0,
            },
        )

    r = viet_lai(bang, nc, llm(), giong)
    p["loai_truoc"] = "tu_van"

    # Hoi ton kho KEM nhu cau -> van tu van binh thuong nhung phai ghi chu ro
    # phan ton kho thieu nguon (khong lam nhu cau hoi do chua ton tai).
    text_cuoi = r["text"]
    if hoi_ton_kho(t.tin_nhan):
        text_cuoi += ("\n\n(Về tồn kho: dữ liệu em đang có chưa gồm tồn kho theo "
                      "khu vực — cần nối Stock API — nên em chưa xác nhận được còn "
                      "hàng ở đâu ạ.)")

    return TraLoi(
        phien_id=ma,
        loai="tu_van",
        text=text_cuoi,
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
            "giong": giong,
        },
    )
