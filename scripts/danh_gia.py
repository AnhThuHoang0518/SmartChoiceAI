# -*- coding: utf-8 -*-
"""Chay bo tinh huong khach that -> do so lieu dua len slide.

Chay:  python scripts/danh_gia.py

Do 4 thu de bai cham diem truc tiep:
  1. Ty le hieu dung o nhu cau  (tieu chi 'hieu nhu cau that')
  2. So cau hoi trung binh      (tieu chi 'hoi nguoc thong minh' - it ma trung)
  3. Ket cuc dung kich ban      (tu van / tu choi dung luc / bao het may)
  4. Thoi gian phan hoi         (moc <3s hoi nguoc, <5s tu van)

Mac dinh chay voi LLM_NHA_CUNG_CAP=luat (khong goi mang, khong ton credit,
CI chay duoc). Muon do ca chat luong van LLM that thi bo env do di.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("LLM_NHA_CUNG_CAP", "luat")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402

DATASET = Path("evaluations/datasets/tinh_huong_may_lanh.json")
KET_QUA = Path("evaluations/results/bao_cao_danh_gia.md")


def so_sanh_o(ky_vong: dict, thuc_te: dict) -> tuple[int, int, list[str]]:
    """Dem o dung / tong o ky vong. 'uu_tien_chua' = kiem tra tap con."""
    dung, tong, loi = 0, 0, []
    for k, v in ky_vong.items():
        tong += 1
        if k == "uu_tien_chua":
            co = set(thuc_te.get("uu_tien", []))
            if set(v) <= co:
                dung += 1
            else:
                loi.append(f"uu_tien thieu {set(v) - co}")
        elif thuc_te.get(k) == v or (
            isinstance(v, (int, float)) and thuc_te.get(k) is not None
            and abs(float(thuc_te[k]) - float(v)) < 0.01
        ):
            dung += 1
        else:
            loi.append(f"{k}: muon {v!r} duoc {thuc_te.get(k)!r}")
    return dung, tong, loi


def chay_tinh_huong(c: TestClient, th: dict, mac_dinh: dict) -> dict:
    tra_loi = {**mac_dinh, **th.get("tra_loi", {})}
    ket = {"ten": th["ten"], "so_cau_hoi": 0, "ms": [], "loi": [], "da_dung_lac_de": False}

    r = c.post("/api/chat", json={"tin_nhan": th["tin_dau"]}).json()
    ket["ms"].append(r["thong_ke"]["ms"])
    pid = r["phien_id"]

    for _ in range(8):                                   # tran cung chong lap vo tan
        if r["loai"] != "cau_hoi":
            break
        ket["so_cau_hoi"] += 1

        # Tinh huong 'lac de': cau tra loi dau tien co tinh vo nghia, de kiem
        # bot co doi loi + kem vi du khi hoi lai khong.
        if th.get("lac_de_truoc") and not ket["da_dung_lac_de"]:
            ket["da_dung_lac_de"] = True
            dap = th["lac_de_truoc"]
        else:
            # Bot dang hoi o nao? Suy tu text (template cung nen so khop duoc).
            o_dang_hoi = _doan_o(r["text"])
            dap = tra_loi.get(o_dang_hoi, "khong biet")

        r = c.post("/api/chat", json={"tin_nhan": dap, "phien_id": pid}).json()
        ket["ms"].append(r["thong_ke"]["ms"])

        if th.get("ky_vong_hoi_lai_co_vi_du") and ket["da_dung_lac_de"] \
                and r["loai"] == "cau_hoi" and "ví dụ" not in r["text"] \
                and "hoi_lai_ok" not in ket:
            # cau hoi ngay sau cau lac de PHAI kem vi du
            ket["loi"].append("hoi lai khong kem vi du")
        elif th.get("ky_vong_hoi_lai_co_vi_du") and "ví dụ" in r.get("text", ""):
            ket["hoi_lai_ok"] = True

    # Cau tiep noi SAU khi da tu van xong ("neu giam con 10 trieu?") - kiem
    # duong DOI Y: o phai duoc ghi de, khong duoc lang le giu gia tri cu.
    for buoc in th.get("tiep_theo", []):
        r = c.post("/api/chat", json={"tin_nhan": buoc["tin"], "phien_id": pid}).json()
        ket["ms"].append(r["thong_ke"]["ms"])
        kvl = buoc.get("ky_vong_loai")
        if kvl and kvl != "bat_ky_khong_loi" and r["loai"] != kvl:
            ket["loi"].append(f"tiep noi: muon {kvl} duoc {r['loai']}")
        if "ky_vong_o" in buoc:
            d2, t2, l2 = so_sanh_o(buoc["ky_vong_o"], r.get("o_nhu_cau", {}))
            ket["o_dung"] = ket.get("o_dung", 0) + d2
            ket["o_tong"] = ket.get("o_tong", 0) + t2
            ket["loi"] += [f"tiep noi: {x}" for x in l2]

    ket["loai_cuoi"] = r["loai"]
    ket["text_cuoi"] = r["text"][:120]

    kv_loai = th["ky_vong_loai"]
    if kv_loai != "bat_ky_khong_loi" and r["loai"] != kv_loai:
        ket["loi"].append(f"ket cuc: muon {kv_loai} duoc {r['loai']}")
    if not r["text"].strip():
        ket["loi"].append("text rong")
    if ket["so_cau_hoi"] > th.get("toi_da_cau_hoi", 8):
        ket["loi"].append(f"hoi {ket['so_cau_hoi']} cau > tran {th['toi_da_cau_hoi']}")

    if "ky_vong_o" in th:
        d, t, l = so_sanh_o(th["ky_vong_o"], r.get("o_nhu_cau", {}))
        ket["o_dung"], ket["o_tong"] = d, t
        ket["loi"] += l
    return ket


def _doan_o(text: str) -> str:
    """Map cau hoi template -> ten o. Template cung nen map cung duoc."""
    t = text.lower()
    if "bao nhiêu" in t and "m²" in t:
        return "dien_tich_m2"
    if "dự tính" in t or "ngân sách" in t:
        return "ngan_sach_max"
    if "nắng" in t:
        return "co_nang"
    if "phòng ngủ hay" in t or "phòng ngủ" in t and "phòng khách" in t:
        return "loai_phong"
    if "khu vực" in t or "tỉnh" in t:
        return "khu_vuc"
    if "diện tích" in t:
        return "dien_tich_m2"
    return "?"


def main() -> None:
    du_lieu = json.loads(DATASET.read_text(encoding="utf-8"))
    c = TestClient(app)

    ket = [chay_tinh_huong(c, th, du_lieu["tra_loi_mac_dinh"]) for th in du_lieu["tinh_huong"]]

    dat = [k for k in ket if not k["loi"]]
    o_dung = sum(k.get("o_dung", 0) for k in ket)
    o_tong = sum(k.get("o_tong", 0) for k in ket)
    hoi = [k["so_cau_hoi"] for k in ket if k["loai_cuoi"] == "tu_van"]
    moi_ms = [m for k in ket for m in k["ms"]]

    dong = [
        "# Bao cao danh gia — bo tinh huong may lanh",
        f"- Ngay chay: {time.strftime('%Y-%m-%d %H:%M')}",
        f"- LLM: {os.getenv('LLM_NHA_CUNG_CAP', 'gemini')}",
        "",
        f"| Chi so | Gia tri |",
        f"|---|---|",
        f"| Tinh huong DAT | **{len(dat)}/{len(ket)}** |",
        f"| O nhu cau trich dung | **{o_dung}/{o_tong}** ({100*o_dung/max(o_tong,1):.0f}%) |",
        f"| So cau hoi TB de ra tu van | **{sum(hoi)/max(len(hoi),1):.1f}** |",
        f"| Phan hoi cham nhat | **{max(moi_ms)}ms** (moc de bai: <5000ms) |",
        "",
        "## Chi tiet",
        "",
        "| Tinh huong | Ket cuc | Hoi | Loi |",
        "|---|---|---|---|",
    ]
    for k in ket:
        dong.append(
            f"| {k['ten']} | {k['loai_cuoi']} | {k['so_cau_hoi']} | "
            + ("; ".join(k["loi"]) if k["loi"] else "—") + " |"
        )

    KET_QUA.parent.mkdir(parents=True, exist_ok=True)
    KET_QUA.write_text("\n".join(dong), encoding="utf-8")

    print("\n".join(dong))
    print(f"\n=> Da luu {KET_QUA}")
    if len(dat) < len(ket):
        print(f"\nCHUA DAT: {len(ket)-len(dat)} tinh huong co loi - xem bang tren.")
        sys.exit(1)


if __name__ == "__main__":
    main()
