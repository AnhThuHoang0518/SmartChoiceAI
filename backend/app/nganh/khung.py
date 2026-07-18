# -*- coding: utf-8 -*-
"""KHUNG NGANH GENERIC - de "them nganh = them 1 config + 1 parser" thanh su that.

Bai toan: tu lanh (vertical thu 2) ton ~330 dong code rieng. Nhan kieu do cho
12 nganh con lai la ~4.000 dong lap - bao tri chet. Khung nay rut phan CHUNG:

  - Nap CSV da chuan hoa -> san pham + Nguon tung truong (badge UI + hau kiem)
  - Trich o nhu cau theo REGEX trong config (+ ngan sach/bo ngan sach dung chung,
    tra loi cut lun theo ngu canh o vua hoi)
  - Loc cung theo config: khoang hang cong bo / gia tran / kich thuoc toi da
    (thieu so -> BO + DEM de noi that, khong doan) / khop ten
  - Cham diem + trade-off theo truc trong config
  - Serialize bang ket qua cho LLM (di qua viet_lai.mo_ta_nhu_cau)

Moi nganh con lai chi can:
  1. configs/nganh/<ten>.json  - o nhu cau, luat loc, truc cham, cau hoi
  2. scripts/nap_dmx_gia_dung.py them 1 muc parse sheet -> processed csv

May lanh + tu lanh DE NGUYEN vertical rieng (dang chay on tren production -
khong dong vao thu da chay ngay truoc gio cham). Hop nhat sau hackathon.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from backend.app.core.chuan_hoa_tv import bo_dau, bo_so_dien_thoai, chuan_hoa, dem_nguoi
from backend.app.schemas.ket_qua import (
    BangKetQua,
    LyDoLoai,
    Nguon,
    TrucSoSanh,
    UngVien,
    dong_so_sanh,
)
from backend.app.services.parse_dmx import parse_gia


class SanPhamChung(BaseModel):
    ma_sp: str
    ten: str
    hang: str
    gia: int
    gia_goc: int
    so: dict[str, float | None] = Field(default_factory=dict)     # cot so
    chu: dict[str, str] = Field(default_factory=dict)             # cot chuoi
    nguon: dict[str, Nguon] = Field(default_factory=dict)


class NhuCauChung(BaseModel):
    gia_tri: dict[str, float | str | None] = Field(default_factory=dict)
    uu_tien: list[str] = Field(default_factory=list)

    def lay(self, o: str):
        return self.gia_tri.get(o)

    def dump(self) -> dict:
        d = {k: v for k, v in self.gia_tri.items() if v is not None}
        d["uu_tien"] = self.uu_tien
        return d


def _ng(truong, gia_tri, ma, tu, suy_luan=False,
        lay_luc: str | None = None) -> Nguon:
    return Nguon(truong=truong, gia_tri=str(gia_tri), nguon=tu,
                 lay_luc=lay_luc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 ma_sp=ma, suy_luan=suy_luan)


class Nganh:
    """Mot nganh hang chay tren khung. Khoi tao tu file config JSON."""

    def __init__(self, duong_dan_cfg: str | Path):
        self.cfg = json.loads(Path(duong_dan_cfg).read_text(encoding="utf-8"))
        self.ten = self.cfg["ten_nganh"]
        self.ten_hien_thi = self.cfg["ten_hien_thi"]
        self._ds: list[SanPhamChung] | None = None

    # ── nhan dien nganh trong cau khach ─────────────────────────────────────
    def vi_tri_khop(self, text: str) -> tuple[int, int] | None:
        """Tra (vi tri, -do dai) cua tu khoa xuat hien som nhat trong cau.

        Registry sap theo ten file khong mang y nghia nghiep vu. Chon theo vi
        tri nguoi dung neu san pham gi truoc se tranh 'tablet ... man hinh lon'
        bi file man_hinh (dung truoc may_tinh_bang) cuop router.
        """
        kd = bo_dau(text or "").lower()
        khop = []
        for tu_khoa in self.cfg["tu_khoa_nganh"]:
            if m := re.search(rf"\b{tu_khoa}\b", kd):
                khop.append((m.start(), -(m.end() - m.start())))
        return min(khop) if khop else None

    def khop(self, text: str) -> bool:
        return self.vi_tri_khop(text) is not None

    def yeu_cau_khong_co_du_lieu(self, text: str) -> dict | None:
        """Yeu cau bat buoc ma config xac nhan catalog CHUA co field.

        Day la cua chan truoc xep hang: gap field nay thi tra thieu du lieu,
        tuyet doi khong lay RAM/SSD de suy ra GPU hay mot thuoc tinh khac.
        """
        kd = bo_dau(text or "").lower()
        for spec in self.cfg.get("yeu_cau_khong_co_du_lieu", []):
            if any(re.search(mau, kd) for mau in spec.get("mau", [])):
                return spec
        return None

    # ── catalog ─────────────────────────────────────────────────────────────
    def catalog(self) -> list[SanPhamChung]:
        if self._ds is not None:
            return self._ds
        p = Path(self.cfg["csv_that"])
        if not p.exists():
            p = Path(self.cfg["csv_mau"])
        if not p.exists():
            self._ds = []
            return self._ds
        lay_luc = datetime.fromtimestamp(
            p.stat().st_mtime, timezone.utc
        ).isoformat(timespec="seconds")

        cot_so = self.cfg["cot_so"]        # {ten_cot: {"nguon": "...", "ro": "..."}}
        cot_chu = self.cfg.get("cot_chu", {})
        ds = []
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ma = r["ma_sp"]
                gia, gia_goc = parse_gia(r.get("gia_goc"), r.get("gia"))
                if gia is None:
                    continue
                gia_goc = gia_goc or gia
                so, nguon = {}, {
                    "gia": _ng("gia", gia, ma, "catalog:Giá bán", lay_luc=lay_luc),
                    "gia_goc": _ng("gia_goc", gia_goc, ma, "catalog:Giá gốc",
                                    lay_luc=lay_luc),
                }
                for c, meta in cot_so.items():
                    v = None
                    s = (r.get(c) or "").strip()
                    if s:
                        try:
                            v = float(s)
                        except ValueError:
                            v = None
                    so[c] = v
                    if v is not None:
                        nguon[c] = _ng(c, v, ma, meta["nguon"], lay_luc=lay_luc)
                chu = {}
                # 'qua' (khuyen mai qua) doc tu dong moi nganh - mock khong co
                # cot nay thi thoi, khong loi
                if (r.get("qua") or "").strip():
                    chu["qua"] = r["qua"].strip()
                    nguon["qua"] = _ng("qua", chu["qua"], ma,
                                        "catalog:khuyến mãi quà", lay_luc=lay_luc)
                for c, meta in cot_chu.items():
                    chu[c] = (r.get(c) or "").strip()
                    if chu[c]:
                        nguon[c] = _ng(c, chu[c], ma, meta["nguon"], lay_luc=lay_luc)
                ds.append(SanPhamChung(ma_sp=ma, ten=r["ten"], hang=r["hang"],
                                       gia=gia, gia_goc=gia_goc,
                                       so=so, chu=chu, nguon=nguon))
        self._ds = ds
        return ds

    # ── trich o nhu cau (luat trong config, khong LLM) ──────────────────────
    def trich(self, text: str, cu: NhuCauChung | None = None,
              o_dang_cho: str | None = None) -> NhuCauChung:
        text = bo_so_dien_thoai(text)
        t = chuan_hoa(text)
        kd = bo_dau(t).lower()
        nc = (cu or NhuCauChung()).model_copy(deep=True)

        # dem thanh phan gia dinh TRUOC: '2 nguoi lon 1 em be' phai ra 3,
        # khong de regex '(\d) nguoi' cua config chup mat so 2
        if "so_nguoi" in self.cfg["o_nhu_cau"] and nc.lay("so_nguoi") is None \
                and (dn := dem_nguoi(text)):
            nc.gia_tri["so_nguoi"] = float(dn)

        for o, spec in self.cfg["o_nhu_cau"].items():
            if nc.lay(o) is not None:
                continue
            for mau in spec.get("trich", []):
                m = re.search(mau, kd)
                if m:
                    v = m.group(1).replace(",", ".")
                    nc.gia_tri[o] = float(v) if spec["kieu"] == "so" else v
                    break
            # trich_gan: khop mau -> GAN gia tri co dinh (khong bat group).
            # Dung cho o kieu "khach co can X khong": '4g/5g' -> can sim.
            if nc.lay(o) is None:
                for tg in spec.get("trich_gan", []):
                    if re.search(tg["mau"], kd):
                        nc.gia_tri[o] = tg["gia_tri"]
                        break

        # ngan sach dung chung (chuan_hoa da doi 15tr -> 15000000).
        # Khach noi so moi la GHI DE so cu ("thoi lay tam 5tr thoi") - giu
        # lang le so cu la bug doi y kinh dien.
        m = re.search(r"(?:duoi|khoang|tam|toi da|max|gia)\s*([\d]{6,})", kd) \
            or re.search(r"\b([\d]{6,})\b(?!\s*(?:mah|gb|kwh|nit|w\b))", kd)
        if m:
            nc.gia_tri["ngan_sach_max"] = float(m.group(1))

        for ut in self.cfg["truc_cham"]:
            if any(re.search(m, kd) for m in ut.get("trich_uu_tien", [])) \
                    and ut["uu_tien"] not in nc.uu_tien:
                nc.uu_tien.append(ut["uu_tien"])

        # tra loi cut lun: go moi so khi dang duoc hoi dung o do
        if o_dang_cho and nc.lay(o_dang_cho) is None:
            if re.fullmatch(r"[\d.,]+", kd.strip()):
                nc.gia_tri[o_dang_cho] = float(kd.strip().replace(",", "."))
        return nc

    def thieu_bat_buoc(self, nc: NhuCauChung) -> list[str]:
        bb = [o for o, s in self.cfg["o_nhu_cau"].items() if s.get("bat_buoc")]
        return [o for o in bb + ["ngan_sach_max"] if nc.lay(o) is None]

    def cau_hoi(self, o: str, lap_lai: bool) -> str:
        if o == "ngan_sach_max":
            spec = self.cfg["cau_hoi_ngan_sach"]
        else:
            spec = self.cfg["o_nhu_cau"][o]
        return spec["cau_hoi_lap" if lap_lai and "cau_hoi_lap" in spec else "cau_hoi"]

    # ── loc cung ────────────────────────────────────────────────────────────
    def loc_cung(self, ds, nc) -> tuple[list, list, int]:
        """Tra (con_lai, bi_loai[(sp, ly_do, chi_tiet)], so_thieu_du_lieu_bi_bo)."""
        con, loai, thieu = [], [], 0
        for s in ds:
            hong = None
            vh = nc.lay("hang")
            if vh and bo_dau(s.hang).lower() != bo_dau(str(vh)).lower():
                hong = ("hang", f"khác hãng {vh}")
            for luat in self.cfg["loc_cung"] if hong is None else []:
                k = luat["kieu"]
                if k == "khoang_hang_cong_bo":
                    v = nc.lay(luat["o"])
                    if v is None:
                        continue
                    lo, hi = s.so.get(luat["cot_min"]), s.so.get(luat["cot_max"])
                    if lo is None or hi is None or not (lo <= v <= hi):
                        hong = (luat["ly_do"],
                                f"hãng công bố {lo:.0f}-{hi:.0f} {luat['don_vi']}, "
                                f"không khớp {v:.0f}" if lo is not None else
                                "hãng không công bố thông số này")
                        break
                elif k == "ngan_sach":
                    v = nc.lay("ngan_sach_max")
                    if v and s.gia > v:
                        hong = ("ngan_sach", "vượt ngân sách")
                        break
                elif k in ("toi_da", "toi_thieu"):
                    v = nc.lay(luat["o"])
                    if v is None:
                        continue
                    sv = s.so.get(luat["cot"])
                    if sv is None:
                        # thieu so -> khong xac nhan duoc -> BO + DEM, khong doan
                        hong = ("__thieu__", "")
                        break
                    if (k == "toi_da" and sv > v) or (k == "toi_thieu" and sv < v):
                        dau = ">" if k == "toi_da" else "<"
                        hong = (luat["ly_do"], f"{sv:g} {dau} {v:g} {luat['don_vi']}")
                        break
                elif k == "khop_ten":
                    v = nc.lay(luat["o"])
                    # So khop BO DAU ca hai phia: khach go 'bom nhiet' (khong dau,
                    # tu regex trich) con catalog ghi 'Sấy bơm nhiệt' (co dau) -
                    # khong bo dau la loai oan sach (bug tim ra khi test TC-029).
                    if v and bo_dau(str(v)).lower() not in bo_dau(s.chu.get(luat["cot"], "")).lower():
                        hong = (luat["ly_do"], s.chu.get(luat["cot"], ""))
                        break
            if hong is None:
                con.append(s)
            elif hong[0] == "__thieu__":
                thieu += 1
            else:
                loai.append((s, hong[0], hong[1]))
        return con, loai, thieu

    # ── cham diem + top 3 ───────────────────────────────────────────────────
    def xep_hang(self, ds, nc) -> tuple[BangKetQua, int]:
        con, bi_loai, thieu = self.loc_cung(ds, nc)

        truc = self.cfg["truc_cham"]
        ts = {t["uu_tien"]: 0.4 for t in truc if t["uu_tien"] in nc.uu_tien}
        for t in truc:
            if t.get("mac_dinh"):
                ts.setdefault(t["uu_tien"], t["mac_dinh"])
        tong = sum(ts.values()) or 1.0
        ts = {k: v / tong for k, v in ts.items()}
        theo_ten = {t["uu_tien"]: t for t in truc}

        def lay(t, s):
            return float(s.gia) if t["cot"] == "gia" else s.so.get(t["cot"])

        def chuan(vals, thap_tot):
            co = [v for v in vals if v is not None]
            if not co or max(co) == min(co):
                return [0.5] * len(vals)
            lo, hi = min(co), max(co)
            return [0.5 if v is None else
                    (1 - (v - lo) / (hi - lo) if thap_tot else (v - lo) / (hi - lo))
                    for v in vals]

        diem = [0.0] * len(con)
        for u, w in ts.items():
            t = theo_ten[u]
            for i, d in enumerate(chuan([lay(t, s) for s in con], t["thap_tot"])):
                diem[i] += w * d
        xep = sorted(zip(con, diem), key=lambda x: -x[1])
        # Khu trung TEN trong top 3: sheet dien tu co nhieu SKU cho 1 model
        # (bien the mau sac) - khach nhin ten, 'Xiaomi 190123' xuat hien 3 lan
        # trong top 3 la vo nghia (bug tim ra khi test tablet tren data that).
        # Giu ban diem cao nhat cua moi ten.
        da_thay, xep_khu_trung = set(), []
        for s, d in xep:
            if s.ten in da_thay:
                continue
            da_thay.add(s.ten)
            xep_khu_trung.append((s, d))
        xep = xep_khu_trung
        top = [s for s, _ in xep[:3]]

        ung = []
        for s, d in xep[:3]:
            hon, kem = [], []
            for u in ts:
                t = theo_ten[u]
                v = lay(t, s)
                doi = [o for o in top if o.ma_sp != s.ma_sp and lay(t, o) is not None]
                if v is None or not doi:
                    continue
                best = (min if t["thap_tot"] else max)(doi, key=lambda o: lay(t, o))
                bv = lay(t, best)
                muc = hon if ((v < bv) if t["thap_tot"] else (v > bv)) else (kem if v != bv else None)
                if muc is not None:
                    muc.append(TrucSoSanh(truc=t["ten"], cua_minh=t["fmt"].format(v),
                                          doi_thu=f"{best.ten} {t['fmt'].format(bv)}"))
            ung.append(UngVien(ma_sp=s.ma_sp, ten=s.ten, gia=s.gia, diem=round(d, 4),
                               hon=hon, kem=kem, nguon=list(s.nguon.values())))

        loai_nb = None
        chinh = self.cfg["loc_cung"][0].get("ly_do")
        cand = [x for x in bi_loai if x[1] == chinh]
        if cand:
            sp, ly, ct = min(cand, key=lambda x: x[0].gia)
            loai_nb = LyDoLoai(ma_sp=sp.ma_sp, ten=sp.ten, ly_do=ly, chi_tiet=ct)

        return BangKetQua(top3=ung, loai_noi_bat=loai_nb,
                          tong_truoc_loc=len(ds), con_lai_sau_loc=len(con)), thieu

    # ── serialize cho LLM ───────────────────────────────────────────────────
    def bang_thanh_chu(self, bang: BangKetQua, nc: NhuCauChung, thieu: int) -> str:
        d = [f"NHU CẦU KHÁCH ({self.ten_hien_thi.upper()})"]
        for o, spec in self.cfg["o_nhu_cau"].items():
            v = nc.lay(o)
            if v is not None:
                d.append(spec["nhan"].format(v))
        if nc.lay("hang"):
            d.append(f'chỉ xét hãng {nc.lay("hang")}')
        ns = nc.lay("ngan_sach_max")
        if ns and ns >= 10**11:
            d.append("KHÔNG giới hạn ngân sách")
        elif ns:
            from backend.app.core.nhan_truong import tien_chu
            d.append(f"ngân sách {tien_chu(ns)}")

        ra = [", ".join(d), "",
              f"Đã lọc {bang.tong_truoc_loc} máy còn {bang.con_lai_sau_loc} phù hợp.",
              "", "TOP 3:"]
        hien_thi = self.cfg.get("hien_thi_thong_so", [])
        for i, u in enumerate(bang.top3, 1):
            ra.append(f"{i}. {u.ten} — giá {u.gia:,d}đ".replace(",", "."))
            th = {n.truong: n.gia_tri for n in u.nguon}
            chi_tiet = [ht["fmt"].format(float(th[ht["cot"]]))
                        for ht in hien_thi
                        if th.get(ht["cot"]) not in (None, "None", "")]
            if chi_tiet:
                ra.append("   " + " · ".join(chi_tiet))
            for h in u.hon:
                ra.append(dong_so_sanh(h, la_hon=True))
            for k in u.kem:
                ra.append(dong_so_sanh(k, la_hon=False))
        if bang.loai_noi_bat:
            ra += ["", f"KHÔNG ĐỀ XUẤT: {bang.loai_noi_bat.ten} — {bang.loai_noi_bat.chi_tiet}"]
        if thieu:
            ra += ["", f"LƯU Ý PHẢI NÓI: {thieu} máy khác thiếu dữ liệu để đối chiếu "
                       "ràng buộc của khách — em không xác nhận bừa."]
        return "\n".join(ra)


# ── Registry: cac nganh chay tren khung ─────────────────────────────────────

_REGISTRY: list[Nganh] | None = None


def cac_nganh() -> list[Nganh]:
    global _REGISTRY
    if _REGISTRY is None:
        thu_muc = Path("configs/nganh")
        _REGISTRY = [Nganh(p) for p in sorted(thu_muc.glob("*.json"))] \
            if thu_muc.exists() else []
    return _REGISTRY


def tim_nganh(text: str) -> Nganh | None:
    ds = tim_cac_nganh(text)
    return ds[0] if ds else None


def tim_cac_nganh(text: str) -> list[Nganh]:
    """Tat ca nganh duoc nhac, xep theo vi tri tu khoa trong cau."""
    co = []
    for ng in cac_nganh():
        if (vi_tri := ng.vi_tri_khop(text)) is not None:
            co.append((vi_tri, ng.ten, ng))
    return [ng for _, _, ng in sorted(co, key=lambda x: (x[0], x[1]))]


def nganh_theo_ten(ten: str) -> Nganh | None:
    for ng in cac_nganh():
        if ng.ten == ten:
            return ng
    return None
