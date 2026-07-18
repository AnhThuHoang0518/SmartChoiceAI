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
from backend.app.agents.trich_o_nhu_cau import trich, trich_bang_luat
from backend.app.agents.viet_lai import viet_lai
from backend.app.core import phien
from backend.app.core.hoi_tiep_noi import (
    canh_bao_may_lanh_chua_co_nguon,
    giai_thich_truong,
    tieu_chi_may_lanh_chua_co_nguon,
    tra_loi_tiet_kiem_dien,
)
from backend.app.core.hoi_tiep_san_pham import tra_loi_truong_san_pham
from backend.app.core.chuan_hoa_tv import (
    bo_dau,
    bo_hang,
    bo_ngan_sach,
    can_hoi_lam_ro_nganh,
    cau_hoi_cong_suat,
    chi_la_xac_nhan_dong_y,
    co_nganh_may_lanh,
    co_nganh_tu_lanh,
    goi_y_may_lanh_tu_nhu_cau_lam_mat,
    hoi_chu_quan,
    hoi_hang,
    hoi_vi_sao_xep,
    hoi_khuyen_mai,
    hoi_ton_kho,
    muc_gia,
    nganh_ngoai_pham_vi,
    so_dien_thoai_trong,
    trich_hang,
    tra_loi_xac_nhan_goi_y,
    tu_ky_thuat_trong,
    yeu_cau_so_sanh,
    yeu_cau_thong_so,
)
from backend.app.core.nhan_truong import dinh_dang, tien_chu
from backend.app.schemas.nhu_cau import UuTien

# Sentinel "khong gioi han ngan sach": khach noi 'bao nhieu cung duoc' thi day
# van la MOT cau tra loi cho o ngan sach (o bat buoc) - khong the de None vi se
# bi hoi lai. Moi cho hien thi phai doi thanh chu 'khong gioi han'.
KHONG_GIOI_HAN = 10**12
from backend.app.ranking.xep_hang import cfg, xep_hang
from backend.app.services.catalog import tai_catalog
from backend.app.services.chinh_sach import hoi_chinh_sach, tra_loi_chinh_sach
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
    # Chip goi y cau tiep theo - khach bam gui luon, khoi nghi cau. Code chon
    # theo ngu canh (dang hoi o nao / vua tu van xong), KHONG qua LLM.
    goi_y: list[str] = Field(default_factory=list)


# Chip goi y theo o dang hoi. "Tầm trung"/"Giá rẻ thôi" di qua muc_gia ->
# nguong tinh tu phan bo gia THAT cua nganh (tercile), khong bia so.
GOI_Y_O = {
    "ngan_sach_max": ["Tầm trung", "Giá rẻ thôi", "Không giới hạn ngân sách"],
    "dien_tich_m2": ["Phòng 18m²", "Phòng 25m²", "Phòng 30m²"],
    "co_nang": ["Có nắng", "Không nắng"],
    "loai_phong": ["Phòng ngủ", "Phòng khách"],
    "so_nguoi": ["2 người", "4 người", "6 người"],
}


def _goi_y_tu_van(top3, giong: str) -> list[str]:
    ra = []
    if len(top3) >= 2:
        ra.append("So sánh máy 1 và máy 2")
    ra.append("Vì sao chọn máy 1?")
    if giong != "ky_thuat":
        ra.append("Cho xin thông số chi tiết")
    return ra


def _ngan_sach_muc(gia_cac_may: list, muc: str) -> float:
    """'re'/'trung'/'cao' -> nguong tien tu TERCILE gia that cua nganh dang tu
    van. Khong co bang nguong tu che - re = 1/3 gia thap nhat, trung = 2/3."""
    if muc == "cao":
        return float(KHONG_GIOI_HAN)
    gs = sorted(gia_cac_may)
    return float(gs[len(gs) // 3] if muc == "re" else gs[(2 * len(gs)) // 3])


_ANH: dict | None = None


def _anh_sp() -> dict:
    """ma_sp -> URL anh chinh chu dienmayxanh.com (sinh boi scripts/lay_anh_dmx.py,
    doi chieu qua productidweb). Khong co file -> {} - UI giu icon nganh."""
    global _ANH
    if _ANH is None:
        import json as _j
        from pathlib import Path as _P
        f = _P("data/processed/anh_sp.json")
        _ANH = _j.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return _ANH


def _gan_anh(top3: list[dict]) -> list[dict]:
    for u in top3:
        url = _anh_sp().get(str(u.get("ma_sp")))
        if url:
            u["anh_url"] = url
    return top3


def _gia_tri_nguon(ung_vien, truong: str) -> str | None:
    """Lay mot gia tri da co nguon tu bang ket qua; khong doc nguoc catalog."""
    for n in ung_vien.nguon:
        if n.truong == truong and n.gia_tri not in (None, "", "None"):
            return str(n.gia_tri)
    return None


def _so_gon(v: str) -> str:
    try:
        return f"{float(v):g}"
    except (TypeError, ValueError):
        return str(v)


def _nhan_manh_uu_tien_may_lanh(top1, uu_tien_luot: list[UuTien]) -> str:
    """Cau code dam bao tra DUNG trong tam khach vua hoi, ke ca top chi co 1.

    LLM van dien dat phan tong the, nhung khong duoc phep lam mat tieu chi
    'chay em/lam lanh nhanh/tiet kiem dien' vi khong co doi thu de so sanh.
    """
    if not uu_tien_luot:
        return ""
    y = []
    for u in dict.fromkeys(uu_tien_luot):
        if u == UuTien.DO_ON:
            v = _gia_tri_nguon(top1, "do_on_db")
            y.append(
                f"{top1.ten} có độ ồn hãng công bố {_so_gon(v)} dB"
                if v else f"catalog chưa có số độ ồn của {top1.ten}, nên em chưa khẳng định máy chạy êm"
            )
        elif u == UuTien.LAM_LANH_NHANH:
            v = _gia_tri_nguon(top1, "lam_lanh_nhanh")
            y.append(
                f"{top1.ten} có chế độ làm lạnh nhanh"
                if v == "Có" else f"catalog chưa ghi nhận chế độ làm lạnh nhanh của {top1.ten}"
            )
        elif u == UuTien.TIET_KIEM_DIEN:
            v = _gia_tri_nguon(top1, "cspf")
            y.append(
                f"{top1.ten} có CSPF {_so_gon(v)}"
                if v else f"catalog chưa có CSPF của {top1.ten}, nên em chưa khẳng định mức tiết kiệm điện"
            )
        elif u == UuTien.GIA:
            y.append(f"{top1.ten} có giá {tien_chu(top1.gia)}")
    return "Dạ theo đúng tiêu chí anh chị vừa hỏi: " + "; ".join(y) + " ạ." if y else ""


def _xac_nhan_kich_thuoc_tu_lanh(top1, nc) -> str:
    """Noi ro vi sao tủ vuot qua bo loc cho dat, khong chi dua badge ky thuat."""
    if nc.ngang_cm is None:
        return ""
    ngang = _gia_tri_nguon(top1, "ngang_cm")
    if not ngang:  # loc cung da bo tủ thieu ngang; nhanh nay chi la chan an toan
        return ""
    kich_thuoc = [f"ngang {_so_gon(ngang)} cm"]
    for truong, nhan in (("cao_cm", "cao"), ("sau_cm", "sâu")):
        if v := _gia_tri_nguon(top1, truong):
            kich_thuoc.append(f"{nhan} {_so_gon(v)} cm")
    return (
        f"Dạ em đã lọc theo bề ngang chỗ đặt tối đa {nc.ngang_cm:g} cm. "
        f"{top1.ten} có kích thước " + ", ".join(kich_thuoc)
        + f", nên phần thân tủ không vượt bề ngang {nc.ngang_cm:g} cm ạ."
    )


_HANG: set[str] | None = None


def _cac_hang_toan_he() -> set[str]:
    """Moi ten hang co that trong 13 catalog - de nhan ra hang trong cau khach.
    KHONG co danh sach hang tu che: hang khong co trong du lieu thi khong biet."""
    global _HANG
    if _HANG is None:
        from backend.app.nganh.khung import cac_nganh
        from backend.app.nganh.tu_lanh import tai_catalog_tu_lanh
        hang = {s.hang for s in catalog()} | {s.hang for s in tai_catalog_tu_lanh()}
        for ng in cac_nganh():
            hang |= {s.hang for s in ng.catalog()}
        _HANG = {h for h in hang if h}
    return _HANG


def _hang_trong_cau(text: str, ds_nganh, ten_nganh: str):
    """Tra (hang_khop_catalog_nganh | None, cau_tu_choi | None).

    Hang co that o nganh KHAC nhung nganh nay khong ban (vd 'may giat Daikin')
    -> noi that + liet ke hang dang co, khong loc ra 0 may roi do loi ngan sach.
    """
    h = trich_hang(text, _cac_hang_toan_he())
    if not h:
        return None, None
    for s in ds_nganh:
        if bo_dau(s.hang).lower() == bo_dau(h).lower():
            return s.hang, None
    from collections import Counter
    co = ", ".join(k for k, _ in Counter(s.hang for s in ds_nganh).most_common(8))
    return None, (f"Dạ {ten_nganh} bên em chưa có hàng {h} ạ. Các hãng đang có: {co}. "
                  f"Anh/chị xem hãng nào trong số này em lọc ngay ạ?")


def _so_sanh_2_may(t: TinNhan, ma: str, p: dict, t0: float,
                   cap: tuple[int, int]) -> TraLoi:
    """SO SANH TRUC TIEP 2 may trong top 3 vua tu van - de bai ten la 'so sanh
    san pham' nen day la lenh rieng. Bang do CODE dung tu du lieu da luu trong
    phien (moi so co nguon san) - khong qua LLM, khong the bia, tra ve tuc thi.
    """
    top = p["top3_truoc"]
    i, j = cap
    if i >= len(top) or j >= len(top):
        return TraLoi(phien_id=ma, loai="so_sanh",
                      text=f"Dạ bảng gần nhất em chỉ có {len(top)} máy ạ — anh chị chọn "
                           f"trong số đó giúp em nhé (ví dụ: 'so sánh máy 1 và máy 2').",
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0})
    a, b = top[i], top[j]
    tha = {n["truong"]: n["gia_tri"] for n in a["nguon"]}
    thb = {n["truong"]: n["gia_tri"] for n in b["nguon"]}

    dong = [f"Dạ em so nhanh **{a['ten']}** (máy {i + 1}) và **{b['ten']}** (máy {j + 1}) nhé ạ:"]
    rong = (None, "None", "")
    for truong in {**tha, **thb}:          # hop 2 phia - truong chi 1 may co van hien
        va, vb = tha.get(truong), thb.get(truong)
        if va in rong and vb in rong:
            continue
        if truong == "gia_goc" and tha.get("gia") == va and thb.get("gia") == vb:
            continue                       # khong khuyen mai -> gia goc trung gia ban, bo qua
        # Mot may thieu du lieu -> NOI RO "hang khong cong bo", khong lang le
        # giau truong do (giau di la lam bang so sanh dep hon su that).
        if va in rong or vb in rong:
            nhan, x = dinh_dang(truong, vb if va in rong else va)
            trai = "(hãng không công bố)" if va in rong else x
            phai = x if va in rong else "(hãng không công bố)"
            dong.append(f"• {nhan}: {trai}  —  {phai}")
            continue
        nhan, xa = dinh_dang(truong, va)
        _, xb = dinh_dang(truong, vb)
        # Gia tri chu qua dai (vd danh sach dong CPU) lam vo bang - cat gon,
        # chi tiet day du van xem duoc o badge nguon tren card.
        xa = xa if len(xa) <= 60 else xa[:57] + "…"
        xb = xb if len(xb) <= 60 else xb[:57] + "…"
        if xa == xb:
            dong.append(f"• {nhan}: {xa} (bằng nhau)")
        else:
            dong.append(f"• {nhan}: {xa}  —  {xb}")

    chenh = abs(a["gia"] - b["gia"])
    if chenh:
        re_hon = a if a["gia"] < b["gia"] else b
        dong.append("")
        dong.append(f"→ **{re_hon['ten']}** rẻ hơn {chenh:,d}đ.".replace(",", "."))
        dong.append("Anh/chị ưu tiên tiêu chí nào để em chốt giúp một máy ạ?")
    return TraLoi(
        phien_id=ma, loai="so_sanh", text="\n".join(dong),
        top3=[a, b],
        goi_y=["Máy nào đang giảm giá?"] if p.get("nganh") == "may_lanh" else [],
        thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0,
                  "nganh": p.get("nganh")},
    )


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
                           "anh chị cần máy lạnh thì em tư vấn được ngay ạ!",
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0})

    p["nganh"] = "tu_lanh"
    o_cho = p["da_hoi"][-1] if p["da_hoi"] else None
    nc = trich_tu_lanh(t.tin_nhan, p.get("nhu_cau_tl"), o_cho)
    if bo_ngan_sach(t.tin_nhan):
        nc = nc.model_copy(update={"ngan_sach_max": KHONG_GIOI_HAN})
    if nc.ngan_sach_max is None and (mg := muc_gia(t.tin_nhan)):
        nc = nc.model_copy(update={"ngan_sach_max": int(_ngan_sach_muc([s.gia for s in ds], mg))})
    # Doi nganh giua phien: mang ngan sach da chot theo, khong bat khai lai.
    if nc.ngan_sach_max is None and p.get("ngan_sach_chung"):
        nc = nc.model_copy(update={"ngan_sach_max": int(p["ngan_sach_chung"])})
    if nc.ngan_sach_max:
        p["ngan_sach_chung"] = nc.ngan_sach_max
    if bo_hang(t.tin_nhan):
        nc = nc.model_copy(update={"hang": None})
    else:
        h, tu_choi = _hang_trong_cau(t.tin_nhan, ds, "tủ lạnh")
        if tu_choi:
            p["nhu_cau_tl"] = nc
            return TraLoi(phien_id=ma, loai="khong_co_hang", text=tu_choi,
                          thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                                    "cham_llm": 0, "nganh": "tu_lanh"})
        if h:
            nc = nc.model_copy(update={"hang": h})
    p["nhu_cau_tl"] = nc
    p["luc"] = time.time()

    thieu = nc.thieu_bat_buoc()
    if thieu:
        o = thieu[0]
        text = cfg_tl["cau_hoi_lap_lai" if o in p["da_hoi"] else "cau_hoi"][o]
        p["da_hoi"].append(o)
        return TraLoi(phien_id=ma, loai="cau_hoi", text=text,
                      o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
                      goi_y=GOI_Y_O.get(o, []),
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
    text_cuoi = r["text"]
    if xac_nhan := _xac_nhan_kich_thuoc_tu_lanh(bang.top3[0], nc):
        text_cuoi = xac_nhan + "\n\n" + text_cuoi
    p["loai_truoc"] = "tu_van"
    p["top3_truoc"] = _gan_anh([u.model_dump(mode="json") for u in bang.top3])
    return TraLoi(
        phien_id=ma, loai="tu_van", text=text_cuoi,
        o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
        goi_y=_goi_y_tu_van(bang.top3, giong),
        top3=p["top3_truoc"],
        loai_noi_bat=bang.loai_noi_bat.model_dump(mode="json") if bang.loai_noi_bat else None,
        thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 2,
                  "truoc_loc": bang.tong_truoc_loc, "sau_loc": bang.con_lai_sau_loc,
                  "bo_vi_thieu": thieu_kt,
                  "nguon_llm": r["nguon_llm"], "so_lan_chan_bia": r["so_lan_bi_chan"],
                  "loi_da_chan": r["loi_da_chan"], "giong": giong, "nganh": "tu_lanh"},
    )


def _xu_ly_nganh_khung(t: TinNhan, ma: str, p: dict, t0: float, giong: str,
                       nganh) -> TraLoi:
    """Luong tu van cho NGANH CHAY TREN KHUNG (may giat, may say... - moi nganh
    la 1 file configs/nganh/*.json). Cung nhip sale: gom o bat buoc -> loc cung
    theo cong bo hang -> top 3 -> LLM dien dat -> hau kiem theo ro don vi.
    """
    from types import SimpleNamespace

    from backend.app.agents.viet_lai import viet_lai

    ds = nganh.catalog()
    if not ds:
        return TraLoi(phien_id=ma, loai="ngoai_pham_vi",
                      text=f"Dạ dữ liệu {nganh.ten_hien_thi} chưa được nạp trên hệ "
                           "thống này ạ — anh chị cần máy lạnh/tủ lạnh thì em tư vấn ngay ạ!",
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0})

    p["nganh"] = nganh.ten
    khoa = f"nhu_cau_{nganh.ten}"
    o_cho = p["da_hoi"][-1] if p["da_hoi"] else None
    nc = nganh.trich(t.tin_nhan, p.get(khoa), o_cho)
    if bo_ngan_sach(t.tin_nhan):
        nc.gia_tri["ngan_sach_max"] = float(KHONG_GIOI_HAN)
    if nc.lay("ngan_sach_max") is None and (mg := muc_gia(t.tin_nhan)):
        nc.gia_tri["ngan_sach_max"] = _ngan_sach_muc([s.gia for s in ds], mg)
    # Doi nganh giua phien: mang ngan sach da chot theo, khong bat khai lai.
    if nc.lay("ngan_sach_max") is None and p.get("ngan_sach_chung"):
        nc.gia_tri["ngan_sach_max"] = float(p["ngan_sach_chung"])
    if nc.lay("ngan_sach_max"):
        p["ngan_sach_chung"] = nc.lay("ngan_sach_max")
    if bo_hang(t.tin_nhan):
        nc.gia_tri["hang"] = None
    else:
        h, tu_choi = _hang_trong_cau(t.tin_nhan, ds, nganh.ten_hien_thi)
        if tu_choi:
            p[khoa] = nc
            return TraLoi(phien_id=ma, loai="khong_co_hang", text=tu_choi,
                          thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                                    "cham_llm": 0, "nganh": nganh.ten})
        if h:
            nc.gia_tri["hang"] = h
    p[khoa] = nc
    p["luc"] = time.time()

    thieu = nganh.thieu_bat_buoc(nc)
    if thieu:
        o = thieu[0]
        text = nganh.cau_hoi(o, lap_lai=o in p["da_hoi"])
        p["da_hoi"].append(o)
        return TraLoi(phien_id=ma, loai="cau_hoi", text=text,
                      o_nhu_cau=nc.dump(),
                      goi_y=GOI_Y_O.get(o, []),
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                                "cham_llm": 0, "giong": giong, "nganh": nganh.ten})

    bang, thieu_kt = nganh.xep_hang(ds, nc)
    if not bang.top3:
        p["loai_truoc"] = "khong_co_may"
        return TraLoi(phien_id=ma, loai="khong_co_may",
                      text=f"Dạ với các tiêu chí hiện tại em chưa tìm được "
                           f"{nganh.ten_hien_thi} nào phù hợp ạ. Anh/chị có thể nới ngân "
                           "sách hoặc bỏ bớt ràng buộc — em lọc lại ngay ạ.",
                      o_nhu_cau=nc.dump(),
                      thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                                "cham_llm": 0, "nganh": nganh.ten})

    mo_ta = nganh.bang_thanh_chu(bang, nc, thieu_kt)
    # hau_kiem doc thuoc tinh tu nhu_cau qua getattr -> boc dict thanh namespace
    nc_shim = SimpleNamespace(**{k: v for k, v in nc.gia_tri.items() if v is not None})
    r = viet_lai(bang, nc_shim, llm(), giong, mo_ta_nhu_cau=mo_ta)
    p["loai_truoc"] = "tu_van"
    p["top3_truoc"] = _gan_anh([u.model_dump(mode="json") for u in bang.top3])
    return TraLoi(
        phien_id=ma, loai="tu_van", text=r["text"],
        o_nhu_cau=nc.dump(),
        goi_y=_goi_y_tu_van(bang.top3, giong),
        top3=p["top3_truoc"],
        loai_noi_bat=bang.loai_noi_bat.model_dump(mode="json") if bang.loai_noi_bat else None,
        thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 2,
                  "truoc_loc": bang.tong_truoc_loc, "sau_loc": bang.con_lai_sau_loc,
                  "bo_vi_thieu": thieu_kt,
                  "nguon_llm": r["nguon_llm"], "so_lan_chan_bia": r["so_lan_bi_chan"],
                  "loi_da_chan": r["loi_da_chan"], "giong": giong, "nganh": nganh.ten},
    )


class AnhYeuCau(BaseModel):
    anh_b64: str
    dinh_dang: str = "jpeg"


@router.post("/nhin-anh")
def nhin_anh_khach(y: AnhYeuCau) -> dict:
    """Khach chup anh (nhan nang luong may cu, may dang phan van) -> Qwen2.5-VL
    doc -> tra MO TA. UI dua mo ta vao o nhap -> chay flow tu van binh thuong
    (anh chi giup DIEN o nhu cau nhu tin nhan go tay, moi so van qua hau kiem).

    Chua cau hinh FPT -> 503, UI bao khach go tay. Gioi han base64 ~ 6MB.
    """
    import os as _os

    from fastapi import HTTPException

    from backend.app.services.llm import nhin_anh

    khoa = (_os.getenv("LLM_API_KEY") or "").strip()
    if not khoa or (_os.getenv("LLM_NHA_CUNG_CAP") or "").strip().lower() != "fpt":
        raise HTTPException(503, "Tính năng đọc ảnh cần cấu hình FPT")
    if len(y.anh_b64) > 8_000_000:
        raise HTTPException(413, "Ảnh quá lớn — chụp lại nhỏ hơn giúp em ạ")
    try:
        mo_ta = nhin_anh(khoa, y.anh_b64, y.dinh_dang,
                         _os.getenv("VLM_MODEL", "Qwen2.5-VL-7B-Instruct"))
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(503, f"Đọc ảnh lỗi: {e}") from e
    return {"mo_ta": mo_ta}


class DocYeuCau(BaseModel):
    text: str


@router.post("/doc")
def doc_thanh_tieng(y: DocYeuCau):
    """TTS FPT.AI-VITs - theo DUNG tai lieu tren trang model (Inference API):
    client.audio.speech.create(model='FPT.AI-VITs', input=..., voice='std_kimngan',
    response_format='wav') tren base https://mkp-api.fptcloud.com (OpenAI compat)
    -> POST /audio/speech. 9 giong tieng Viet thu am dien vien long tieng.

    Chua cau hinh FPT -> 503, UI tu roi ve giong trinh duyet (van doc duoc).
    Gioi han 400 ky tu: gia $16.5/1M ky tu -> ~1/3 xu moi cau, khong chay lan.
    """
    import os as _os

    import requests as _rq
    from fastapi import HTTPException
    from fastapi.responses import Response as _Resp

    khoa = (_os.getenv("LLM_API_KEY") or "").strip()
    if not khoa or (_os.getenv("LLM_NHA_CUNG_CAP") or "").strip().lower() != "fpt":
        raise HTTPException(503, "TTS chua cau hinh")
    text = (y.text or "").strip()[:400]
    if not text:
        raise HTTPException(400, "text rong")
    try:
        r = _rq.post(
            "https://mkp-api.fptcloud.com/audio/speech",
            headers={"Authorization": f"Bearer {khoa}"},
            json={"model": _os.getenv("TTS_MODEL", "FPT.AI-VITs"),
                  "input": text,
                  "response_format": "wav",
                  "voice": _os.getenv("TTS_GIONG", "std_kimngan")},
            timeout=20,
        )
        r.raise_for_status()
    except Exception as e:                  # noqa: BLE001
        raise HTTPException(503, f"TTS loi: {e}") from e
    return _Resp(content=r.content, media_type="audio/wav")


@router.get("/khuyen-mai")
def khuyen_mai_that() -> list[dict]:
    """Top 4 may lanh giam sau nhat - cho landing page. Gia goc/gia KM lay
    thang tu catalog, KHONG hardcode: landing cung phai theo luat 'moi con so
    deu co nguon' nhu chat."""
    giam = sorted((s for s in catalog() if s.gia < s.gia_goc),
                  key=lambda s: s.gia_goc - s.gia, reverse=True)[:4]
    return [{"ten": s.ten, "gia": s.gia, "gia_goc": s.gia_goc,
             "giam": s.gia_goc - s.gia,
             "qua": getattr(s, "qua", "")[:100],
             "anh_url": _anh_sp().get(str(s.ma_sp), ""),
             "phan_tram": round((1 - s.gia / s.gia_goc) * 100)} for s in giam]


@router.get("/nhan-truong")
def nhan_truong() -> dict:
    """Nhan tieng Viet cho UI (1 nguon su that, frontend khong hardcode):
    truong -> nhan badge, va truc trade-off -> [nhan hon, nhan kem]."""
    from backend.app.core.nhan_truong import NHAN
    from backend.app.schemas.ket_qua import NHAN_TRUC
    return {"truong": {k: v[0] for k, v in NHAN.items()},
            "truc": {k: list(v) for k, v in NHAN_TRUC.items()}}


@router.post("/chat", response_model=TraLoi)
def chat(t: TinNhan) -> TraLoi:
    t0 = time.perf_counter()
    ma = t.phien_id if t.phien_id and phien.lay(t.phien_id) else phien.tao_phien()
    p = phien.lay(ma)

    # PII khong phai o nhu cau va he thong khong co kha nang tu goi lai. Chan
    # truoc chuan hoa tien de 0912345678 khong bao gio thanh ngan sach.
    if so_dien_thoai_trong(t.tin_nhan):
        return TraLoi(
            phien_id=ma,
            loai="bao_mat",
            text=("Dạ em không thể tự gọi điện hoặc tạo yêu cầu gọi lại ạ. "
                  "Anh chị vui lòng không gửi số điện thoại trong đoạn chat; "
                  "em có thể tiếp tục tư vấn sản phẩm ngay tại đây."),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                      "cham_llm": 0, "pii_da_chan": True},
        )

    # Follow-up ve DUNG card thu N phai chay truoc Policy RAG. Neu khong,
    # 'con thu hai co bao hanh gi?' se mat san pham va tra chinh sach chung.
    if hoi_tiep := tra_loi_truong_san_pham(
        t.tin_nhan, p.get("top3_truoc") or []
    ):
        return TraLoi(
            phien_id=ma,
            loai=hoi_tiep["loai"],
            text=hoi_tiep["text"],
            top3=p.get("top3_truoc") or [],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                      "cham_llm": 0, "nganh": p.get("nganh"),
                      "san_pham_thu": hoi_tiep["chi_so"] + 1,
                      "truong_doi_chieu": hoi_tiep["truong"]},
        )

    # Khach bam loi tat / noi chung chung "tu van san pham" -> PHẢI hoi san
    # pham gi truoc. Khong duoc muon nganh cu trong phien (vd vua xem khuyen
    # mai may lanh xong) roi nhay sang hoi ngan sach nhu screenshot demo.
    import re as _re
    kd_chung = bo_dau(t.tin_nhan).lower().strip()
    if _re.fullmatch(r"(?:tu van|chon|mua|tim)(?: giup)? san pham(?: nao)?", kd_chung):
        p["nganh"] = None
        p["xac_nhan_nganh"] = None
        p["da_hoi"].append("nganh")
        return TraLoi(
            phien_id=ma,
            loai="cau_hoi",
            text=cfg()["chao_hoi"]["mau"],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0},
        )

    # Hoi chinh sach/dich vu (bao hanh, doi tra, giao hang/lap dat...) -> tra
    # bang tai lieu private da nap runtime trong data/policies, KHONG qua LLM,
    # KHONG commit noi dung that len repo public.
    if hoi_chinh_sach(t.tin_nhan):
        rcs = tra_loi_chinh_sach(t.tin_nhan)
        return TraLoi(
            phien_id=ma,
            loai=rcs["loai"],
            text=rcs["text"],
            thong_ke={
                "ms": int((time.perf_counter() - t0) * 1000),
                "cham_llm": 0,
                "nguon_chinh_sach": rcs.get("nguon", []),
            },
        )

    # Nganh KHONG co sheet (dien thoai/laptop/tivi) phai tu choi truoc cac
    # intent phu nhu "co hang nao/Samsung khong". Neu khong, cau "đth co
    # Samsung khong" se bi hoi_hang bat va muon nganh cu trong phien (vd may
    # giat Samsung) -> sai nganh.
    from backend.app.nganh.khung import cac_nganh, tim_cac_nganh
    from backend.app.nganh.khung import tim_nganh as _tim
    nganh = nganh_ngoai_pham_vi(t.tin_nhan)
    nganh_ro = _tim(t.tin_nhan)
    if nganh and nganh_ro is None:
        p["xac_nhan_nganh"] = None
        danh_sach = ", ".join(["máy lạnh", "tủ lạnh"] + [n.cfg.get("ten_liet_ke", n.ten_hien_thi) for n in cac_nganh()])
        return TraLoi(
            phien_id=ma,
            loai="ngoai_pham_vi",
            text=cfg()["ngoai_pham_vi"]["mau"].format(nganh=nganh, danh_sach=danh_sach),
            o_nhu_cau=p["nhu_cau"].model_dump(exclude_none=True, mode="json"),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0},
        )

    # Khong xep hang hai nganh co muc dich/chu ky do khac nhau. Chi bat khi
    # cau co y so sanh VA co tu noi 'va/voi/hay', tranh nham cau nhu
    # 'so sanh tablet man hinh lon' thanh so sanh tablet voi monitor.
    kd_router = bo_dau(t.tin_nhan).lower()
    if yeu_cau_so_sanh(t.tin_nhan) is not None \
            and _re.search(r"\b(?:va|voi|hay)\b", kd_router):
        cac_ten_nganh = []
        if co_nganh_may_lanh(t.tin_nhan):
            cac_ten_nganh.append("máy lạnh")
        if co_nganh_tu_lanh(t.tin_nhan):
            cac_ten_nganh.append("tủ lạnh")
        cac_ten_nganh.extend(ng.ten_hien_thi for ng in tim_cac_nganh(t.tin_nhan))
        cac_ten_nganh = list(dict.fromkeys(cac_ten_nganh))
        if len(cac_ten_nganh) >= 2:
            ds_ten = " và ".join(cac_ten_nganh[:2])
            return TraLoi(
                phien_id=ma,
                loai="khac_nganh",
                text=(f"Dạ em không thể xếp hạng trực tiếp {ds_ten} vì chúng "
                      "khác mục đích sử dụng và cách đo điện năng ạ. Anh chị "
                      "chọn một loại sản phẩm trước, em sẽ so các máy cùng "
                      "ngành và cùng điều kiện công bố để kết luận có nguồn."),
                thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                          "cham_llm": 0, "cac_nganh": cac_ten_nganh},
            )

    # Tieu chi bat buoc nhung catalog nganh KHONG CO field: dung truoc moi
    # buoc trich LLM/xep hang. Vi du PC can card roi ma file chi co CPU/RAM/SSD
    # thi khong duoc suy RAM cao => choi game tot.
    from backend.app.nganh.khung import nganh_theo_ten as _nganh_theo_ten_som
    nganh_kiem_thieu = nganh_ro or (
        _nganh_theo_ten_som(p["nganh"]) if p.get("nganh") else None
    )
    if nganh_kiem_thieu is not None:
        yc_thieu = nganh_kiem_thieu.yeu_cau_khong_co_du_lieu(t.tin_nhan)
        if yc_thieu:
            p["nganh"] = nganh_kiem_thieu.ten
            khoa = f"nhu_cau_{nganh_kiem_thieu.ten}"
            o_cho = p["da_hoi"][-1] if p["da_hoi"] else None
            nc_thieu = nganh_kiem_thieu.trich(t.tin_nhan, p.get(khoa), o_cho)
            if bo_ngan_sach(t.tin_nhan):
                nc_thieu.gia_tri["ngan_sach_max"] = float(KHONG_GIOI_HAN)
            if nc_thieu.lay("ngan_sach_max"):
                p["ngan_sach_chung"] = nc_thieu.lay("ngan_sach_max")
            p[khoa] = nc_thieu
            p["luc"] = time.time()
            return TraLoi(
                phien_id=ma,
                loai="thieu_du_lieu",
                text=yc_thieu["text"],
                o_nhu_cau=nc_thieu.dump(),
                thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                          "cham_llm": 0, "nganh": nganh_kiem_thieu.ten,
                          "truong_thieu": yc_thieu["truong"]},
            )

    # ── SUY LUAN CO KIEM CHUNG: chi goi y nganh, chua duoc loc san pham ─────
    # Nganh khach NOI RO luon thang moi suy luan. Trang thai xac_nhan_nganh
    # khong phai o nhu cau va khong duoc dung de xep hang.
    noi_ro_may_lanh = co_nganh_may_lanh(t.tin_nhan)
    noi_ro_tu_lanh = co_nganh_tu_lanh(t.tin_nhan)

    # Tre nho/nhiet do la tieu chi co y nghia nhung catalog may lanh hien
    # chua co field de kiem chung. Nho rieng de canh bao, KHONG dua vao slot
    # va KHONG cho LLM bien thanh ly do "phu hop".
    if noi_ro_may_lanh or p.get("nganh") == "may_lanh":
        moi = tieu_chi_may_lanh_chua_co_nguon(t.tin_nhan)
        if moi:
            da_co = set(p.get("canh_bao_nguon_may_lanh", []))
            p["canh_bao_nguon_may_lanh"] = sorted(da_co | moi)
            kd_thieu = bo_dau(t.tin_nhan).lower()
            la_cau_hoi_rieng = "?" in t.tin_nhan or bool(_re.search(
                r"\b(?:co khong|bao nhieu|the nao|la gi|duoc khong)\b", kd_thieu
            ))
            if p.get("top3_truoc") and la_cau_hoi_rieng:
                p["canh_bao_nguon_may_lanh"] = []
                return TraLoi(
                    phien_id=ma,
                    loai="thieu_du_lieu",
                    text=canh_bao_may_lanh_chua_co_nguon(moi),
                    top3=p["top3_truoc"],
                    thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                              "cham_llm": 0, "nganh": "may_lanh",
                              "truong_thieu": sorted(moi)},
                )
    co_nganh_ro = bool(nganh_ro is not None or noi_ro_may_lanh or noi_ro_tu_lanh)
    dang_cho_xac_nhan = p.get("xac_nhan_nganh")
    # Neu dang cho va khach noi ro MAY LANH, day chinh la mot cach xac nhan.
    # Nganh ro KHAC (tu lanh/may nuoc nong...) thi huy goi y va de router nganh
    # do xu ly, khong ep khach tra loi cau cu.
    nganh_ro_khac_goi_y = bool(nganh_ro is not None or noi_ro_tu_lanh)
    if co_nganh_ro and not (dang_cho_xac_nhan and noi_ro_may_lanh and not nganh_ro_khac_goi_y):
        p["xac_nhan_nganh"] = None

    if dang_cho_xac_nhan and not nganh_ro_khac_goi_y:
        xac_nhan = True if noi_ro_may_lanh else tra_loi_xac_nhan_goi_y(t.tin_nhan)
        if xac_nhan is True:
            p["xac_nhan_nganh"] = None
            p["nganh"] = "may_lanh"
            # "Đúng" trần không chứa thêm nhu cầu nào: hỏi diện tích ngay bằng
            # template code, 0 LLM. Nếu khách nói "đúng, phòng 18m2" thì đi
            # tiếp để bộ trích ô đọc luôn 18m2, không bắt họ nói lại.
            if chi_la_xac_nhan_dong_y(t.tin_nhan):
                phien.ghi(ma, p["nhu_cau"], "dien_tich_m2")
                return TraLoi(
                    phien_id=ma,
                    loai="cau_hoi",
                    text=cfg()["cau_hoi"]["dien_tich_m2"],
                    o_nhu_cau=p["nhu_cau"].model_dump(
                        exclude_none=True, exclude_defaults=True, mode="json"
                    ),
                    goi_y=GOI_Y_O["dien_tich_m2"],
                    thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                              "cham_llm": 0, "nganh": "may_lanh"},
                )
        elif xac_nhan is False:
            p["xac_nhan_nganh"] = None
            p["nganh"] = None
            phien.ghi(ma, p["nhu_cau"], "nganh")
            return TraLoi(
                phien_id=ma,
                loai="cau_hoi",
                text=("Dạ anh chị muốn tìm sản phẩm gì ạ? Anh chị cứ nói tên sản phẩm "
                      "hoặc nhu cầu sử dụng, em sẽ hỏi tiếp để tư vấn đúng ạ."),
                o_nhu_cau=p["nhu_cau"].model_dump(
                    exclude_none=True, exclude_defaults=True, mode="json"
                ),
                thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                          "cham_llm": 0},
            )
        else:
            phien.ghi(ma, p["nhu_cau"])
            return TraLoi(
                phien_id=ma,
                loai="xac_nhan_nganh",
                text=("Dạ em chưa dám tự chọn thay anh chị. Anh chị xác nhận giúp em: "
                      "mình đang tìm máy lạnh để giảm nóng, hay cần sản phẩm khác ạ?"),
                o_nhu_cau=p["nhu_cau"].model_dump(
                    exclude_none=True, exclude_defaults=True, mode="json"
                ),
                goi_y=["Đúng, tìm máy lạnh", "Tôi cần sản phẩm khác"],
                thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                          "cham_llm": 0, "suy_luan": True,
                          "bang_chung": dang_cho_xac_nhan.get("bang_chung")},
            )

    if p.get("nganh") is None and not co_nganh_ro \
            and goi_y_may_lanh_tu_nhu_cau_lam_mat(t.tin_nhan):
        p["xac_nhan_nganh"] = {
            "nganh": "may_lanh",
            "bang_chung": "khách nói nhu cầu giảm nóng/làm mát và có ý định mua",
        }
        phien.ghi(ma, p["nhu_cau"])
        return TraLoi(
            phien_id=ma,
            loai="xac_nhan_nganh",
            text=("Dạ, nghe câu anh chị nói thì có vẻ anh chị đang muốn tìm máy lạnh "
                  "để giảm nóng. Em hiểu vậy có đúng không ạ?"),
            o_nhu_cau=p["nhu_cau"].model_dump(
                exclude_none=True, exclude_defaults=True, mode="json"
            ),
            goi_y=["Đúng, tìm máy lạnh", "Tôi cần sản phẩm khác"],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                      "cham_llm": 0, "suy_luan": True,
                      "bang_chung": "nhu_cau_lam_mat", "nganh_goi_y": "may_lanh"},
        )

    # 'May tiet kiem dien', 'may chay em', 'san pham duoi 10 trieu' dung cho
    # nhieu nganh. Khong co bang chung rieng may lanh thi hoi nganh TRUOC, khong
    # tu lay uu tien/gia roi ngam gan may_lanh.
    if p.get("nganh") is None and not co_nganh_ro \
            and can_hoi_lam_ro_nganh(t.tin_nhan) \
            and giai_thich_truong(t.tin_nhan) is None:
        p["da_hoi"].append("nganh")
        return TraLoi(
            phien_id=ma,
            loai="cau_hoi",
            text=cfg()["chao_hoi"]["mau_lap_lai"],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                      "cham_llm": 0, "can_lam_ro_nganh": True},
        )

    # SO SANH TRUC TIEP 2 may trong top 3 vua tu van - bang do code dung tu
    # du lieu da luu, khong LLM. Chi bat khi phien DA co bang ket qua.
    cap = yeu_cau_so_sanh(t.tin_nhan)
    if cap and p.get("top3_truoc"):
        return _so_sanh_2_may(t, ma, p, t0, cap)

    # "Vi sao chon may nay?" -> giai trinh bang BANG DIEM code da tinh:
    # diem tung may + duoc gi/mat gi + cach tinh. He tu bao chua duoc chinh
    # minh, 0 LLM - day chinh la loi the cua flow do code dieu khien.
    vs = hoi_vi_sao_xep(t.tin_nhan)
    if vs is not None and p.get("top3_truoc"):
        top = p["top3_truoc"]
        if vs >= len(top):
            vs = 0
        u = top[vs]
        dong = [f"Dạ **{u['ten']}** đứng vị trí {vs + 1} vì tổng điểm cao "
                f"{'nhất' if vs == 0 else 'thứ ' + str(vs + 1)} trên các tiêu chí "
                f"anh chị nêu ạ ({u['diem']:.2f}/1):"]
        from backend.app.schemas.ket_qua import nhan_truc
        for h in u.get("hon", []):
            dong.append(f"✓ {nhan_truc(h['truc'], True)}: {h['cua_minh']} (so với {h['doi_thu']})")
        for k in u.get("kem", []):
            dong.append(f"△ {nhan_truc(k['truc'], False)}: {k['cua_minh']} (so với {k['doi_thu']})")
        dong.append("")
        dong.append("Điểm cả bảng: " + " · ".join(
            f"{i + 1}. {x['ten']} ({x['diem']:.2f})" for i, x in enumerate(top)))
        dong.append("Cách tính: mỗi tiêu chí chuẩn hóa 0-1 giữa các máy đã qua lọc, "
                    "nhân trọng số sinh từ chính ưu tiên anh chị nói, cộng lại — "
                    "không có cảm tính, không nhờ AI chấm ạ.")
        return TraLoi(
            phien_id=ma, loai="giai_trinh_xep_hang", text="\n".join(dong),
            goi_y=["So sánh máy 1 và máy 2"] if len(top) >= 2 else [],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0,
                      "nganh": p.get("nganh")},
        )

    # Hoi tiep noi ve field/card vua hien: tra thang bang code tu top da luu.
    # Day sua loi "tu nao it ton dien?" va "sau la gi?" bi xep hang lai roi
    # copy nguyen cau tu van cu.
    if dien := tra_loi_tiet_kiem_dien(
        t.tin_nhan, p.get("top3_truoc") or [], p.get("nganh")
    ):
        text_dien, truong_dien = dien
        return TraLoi(
            phien_id=ma, loai="tra_loi_truong", text=text_dien,
            top3=p.get("top3_truoc") or [],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                      "cham_llm": 0, "nganh": p.get("nganh"),
                      "truong_doi_chieu": truong_dien},
        )
    if text_giai_thich := giai_thich_truong(t.tin_nhan):
        return TraLoi(
            phien_id=ma, loai="giai_thich_truong", text=text_giai_thich,
            top3=p.get("top3_truoc") or [],
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000),
                      "cham_llm": 0, "nganh": p.get("nganh")},
        )

    # "Co nhung hang nao?" -> liet ke hang THAT trong catalog nganh (kem so
    # may dem duoc), khong ke ten hang ngoai du lieu. Chua ro nganh thi de
    # flow chao hoi phia duoi hoi nganh truoc.
    if hoi_hang(t.tin_nhan):
        from backend.app.nganh.khung import nganh_theo_ten as _ntt
        from backend.app.nganh.khung import tim_nganh as _tim_h
        ds_h, ten_h = None, None
        ng_h = _tim_h(t.tin_nhan) or (_ntt(p["nganh"]) if p.get("nganh") else None)
        if ng_h is not None:
            ds_h, ten_h = ng_h.catalog(), ng_h.ten_hien_thi
        elif co_nganh_tu_lanh(t.tin_nhan) or p.get("nganh") == "tu_lanh":
            from backend.app.nganh.tu_lanh import tai_catalog_tu_lanh
            ds_h, ten_h = tai_catalog_tu_lanh(), "tủ lạnh"
        elif co_nganh_may_lanh(t.tin_nhan) or p.get("nganh") == "may_lanh":
            ds_h, ten_h = catalog(), "máy lạnh"
        if ds_h:
            from collections import Counter
            dem = Counter(s.hang for s in ds_h if s.hang)
            ds_hang = " · ".join(f"{k} ({v} máy)" for k, v in dem.most_common(8))
            return TraLoi(
                phien_id=ma, loai="danh_sach_hang",
                text=(f"Dạ {ten_h} bên em đang có {len(dem)} hãng ạ: {ds_hang}."
                      f" Anh/chị muốn xem hãng nào, cho em xin kèm ngân sách để em lọc luôn ạ?"),
                goi_y=[k for k, _ in dem.most_common(3)],
                thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 0},
            )

    # Khach hoi nganh khac (tu lanh, may giat...) -> noi that pham vi, dung lai
    # cau hoi ngan sach nhu robot hong. Phat hien tu demo that.
    # Nganh ngoai pham vi da duoc xu ly som phia tren de khong bi intent phu
    # (hoi hang/khuyen mai...) bat nham.

    ds = catalog()
    o_dang_cho = p["da_hoi"][-1] if p["da_hoi"] else None
    # Trong tam CUA LUOT HIEN TAI tach rieng voi uu tien cong don ca phien.
    # Dung de tra thang cau "con chay em/lam lanh nhanh thi sao?" thay vi nhai
    # lai toan bo nhu cau cu va lam khach thay bot hieu nham.
    uu_tien_luot = trich_bang_luat(t.tin_nhan).uu_tien
    nc = trich(t.tin_nhan, llm(), p["nhu_cau"], o_dang_cho)

    # Khach tuyen bo bo ngan sach ("khong quan tam tien nua") -> ghi nhan la
    # KHONG GIOI HAN. Bug demo that: truoc day cau nay bi bo qua, bot lai
    # nguyen van "trong tam 20 trieu em chua tim duoc..." nhu chua nghe thay.
    if bo_ngan_sach(t.tin_nhan):
        nc = nc.model_copy(update={"ngan_sach_max": KHONG_GIOI_HAN})

    # Khach noi TAM GIA ("tam trung", "gia re thoi") -> nguong tinh tu tercile
    # gia THAT cua nganh, khong bia. Doi nganh giua phien -> mang ngan sach theo.
    if nc.ngan_sach_max is None and (mg := muc_gia(t.tin_nhan)):
        nc = nc.model_copy(update={"ngan_sach_max": int(_ngan_sach_muc([s.gia for s in ds], mg))})
    if nc.ngan_sach_max is None and p.get("ngan_sach_chung") and p.get("nganh") != "may_lanh":
        nc = nc.model_copy(update={"ngan_sach_max": int(p["ngan_sach_chung"])})
    if nc.ngan_sach_max:
        p["ngan_sach_chung"] = nc.ngan_sach_max

    # Loc theo HANG - khach neu ten hang ("co may LG khong") la loc that;
    # "hang nao cung duoc" la xoa loc.
    if bo_hang(t.tin_nhan):
        nc = nc.model_copy(update={"hang": None})
    else:
        h, tu_choi_hang = _hang_trong_cau(t.tin_nhan, ds, "máy lạnh")
        if tu_choi_hang and (co_nganh_may_lanh(t.tin_nhan) or p.get("nganh") == "may_lanh"):
            phien.ghi(ma, nc, None)
            return TraLoi(phien_id=ma, loai="khong_co_hang", text=tu_choi_hang,
                          o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
                          thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1})
        if h:
            nc = nc.model_copy(update={"hang": h})

    # Inverter: rang buoc CUNG (cot 'Loai Inverter' phu 98%). 'non inverter'/
    # 'mono' -> chi may thuong; nhac 'inverter' -> chi may Inverter.
    import re as _re
    kd_inv = bo_dau(t.tin_nhan).lower()
    if _re.search(r"\b(?:non|khong|ko)[ -]?inverter\b|\bmono\b", kd_inv):
        nc = nc.model_copy(update={"can_inverter": False})
    elif _re.search(r"\binverter\b", kd_inv):
        nc = nc.model_copy(update={"can_inverter": True})

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

    # ── ROUTER NGANH: cac nganh chay tren khung generic ─────────────────────
    # Uu tien nganh khach vua nhac; khong nhac thi theo nganh dang do trong
    # phien. May lanh nhac kem thi may lanh thang (nganh chinh cua de bai).
    from backend.app.nganh.khung import nganh_theo_ten, tim_nganh

    if not co_nganh_may_lanh(t.tin_nhan) and not co_nganh_tu_lanh(t.tin_nhan):
        ng = tim_nganh(t.tin_nhan) or (
            nganh_theo_ten(p["nganh"]) if p.get("nganh") else None
        )
        if ng is not None:
            return _xu_ly_nganh_khung(t, ma, p, t0, giong, ng)

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
        # HIEU Y MO (embedding): khach noi MUC DICH ("cho con hoc online") ma
        # keyword khong ra nganh -> goi y nganh gan nghia lam chip. Chi GOI Y,
        # khach van bam chon; khong co FPT -> rong -> giu hanh vi cu.
        from backend.app.agents.hieu_y_mo import goi_y_nganh
        chip = goi_y_nganh(t.tin_nhan) if len(t.tin_nhan.split()) >= 3 else []
        if chip:
            mau = ("Dạ em đoán anh chị đang cần một trong số này — bấm giúp em để "
                   "em tư vấn đúng ạ:")
        return TraLoi(
            phien_id=ma,
            loai="cau_hoi",
            text=mau,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            goi_y=chip,
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1,
                      "giong": giong, "hieu_y_mo": bool(chip)},
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
            top_km = _gan_anh([
                {
                    "ma_sp": s.ma_sp,
                    "ten": s.ten,
                    "gia": s.gia,
                    "diem": round((s.gia_goc - s.gia) / max(s.gia_goc, 1), 4),
                    "hon": [],
                    "kem": [],
                    "nguon": [
                        n.model_dump(mode="json")
                        for n in [s.nguon_cua("gia"), s.nguon_cua("gia_goc"), s.nguon_cua("qua")]
                        if n is not None
                    ],
                }
                for s in giam
            ])
            text = (
                "Dạ em thấy mấy máy lạnh đang giảm sâu nhất trong dữ liệu hiện có đây ạ. "
                "Máy phù hợp hay không còn tùy phòng anh chị — phòng anh chị rộng khoảng "
                "bao nhiêu m² để em lọc máy đang giảm mà vừa phòng ạ?"
            )
        else:
            top_km = []
            text = "Dạ hiện tại em chưa thấy máy nào đang có giá khuyến mãi trong dữ liệu ạ. Anh/chị cho em xin diện tích phòng và ngân sách, em lọc máy giá tốt nhất cho anh chị nhé ạ?"
        phien.ghi(ma, nc, "dien_tich_m2")
        if giam:
            p["loai_truoc"] = "khuyen_mai"
            p["top3_truoc"] = top_km
        return TraLoi(
            phien_id=ma,
            loai="khuyen_mai",
            text=text,
            o_nhu_cau=nc.model_dump(exclude_none=True, mode="json"),
            top3=top_km,
            goi_y=GOI_Y_O.get("dien_tich_m2", []),
            thong_ke={"ms": int((time.perf_counter() - t0) * 1000), "cham_llm": 1,
                      "giong": giong, "nganh": "may_lanh",
                      "truoc_loc": len(ds), "sau_loc": len(giam)},
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
            goi_y=GOI_Y_O.get(hoi.o_hoi, []),
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
                           else tien_chu(ns) if ns else "này"),
                dien_tich=(f"{nc.dien_tich_m2:.0f}" if nc.dien_tich_m2 else "?"),
                gia_thap_nhat=(tien_chu(gia_min) if gia_min else "cao hơn"),
            )
        p["loai_truoc"] = "khong_co_may"
        return TraLoi(
            phien_id=ma,
            loai="khong_co_may",
            text=text,
            goi_y=["Không giới hạn ngân sách"],
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
    p["top3_truoc"] = _gan_anh([u.model_dump(mode="json") for u in bang.top3])

    # Hoi ton kho KEM nhu cau -> van tu van binh thuong nhung phai ghi chu ro
    # phan ton kho thieu nguon (khong lam nhu cau hoi do chua ton tai).
    text_cuoi = r["text"]
    if trong_tam := _nhan_manh_uu_tien_may_lanh(bang.top3[0], uu_tien_luot):
        text_cuoi = trong_tam + "\n\n" + text_cuoi
    if canh_bao := canh_bao_may_lanh_chua_co_nguon(
        p.get("canh_bao_nguon_may_lanh", [])
    ):
        text_cuoi = canh_bao + "\n\n" + text_cuoi
        p["canh_bao_nguon_may_lanh"] = []
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
        goi_y=_goi_y_tu_van(bang.top3, giong),
        top3=p["top3_truoc"],
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
