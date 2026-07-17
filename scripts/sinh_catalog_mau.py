# -*- coding: utf-8 -*-
"""Sinh catalog MAU gia lap -> data/mock/catalog/may_lanh_mau.csv (commit duoc).

Vi sao ton tai: de bai yeu cau nop "du lieu catalog mau", va muc E2 ghi ro
"moi du lieu demo nen duoc gia lap hoac anonymize". Du lieu THAT cua DMX nam
duoi NDA nen bi gitignore -> nguoi cham clone repo ve se KHONG co du lieu.
File mau nay lap lo hong do: nguoi cham chay duoc ngay, con ban demo cong khai
van dung du lieu that (uu tien khi co).

Gia lap nhung GIONG THAT ve cau truc:
  - Phan bo dai pham vi (m2) va gia mo theo thong ke cua file that.
  - Hang gia (Alpha/Bravo/...) - khong dung ten hang that de khoi ai hieu nham
    gia mau la gia that.
  - CO CA dong ban co tinh (do on rong, khong khuyen mai...) - he thong phai
    song voi du lieu ban, va bo test can dong ban de chung minh dieu do.

Seed co dinh -> chay lai ra Y HET, khoi noi "so lieu doi lung tung".
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

RA = Path("data/mock/catalog/may_lanh_mau.csv")

HANG = ("Alpha", "Bravo", "Cosmo", "Delta", "Epsil")

# (pham_vi_min, pham_vi_max, gia_thap_nhat, gia_cao_nhat) - mo theo file that:
# nhieu may nho gia mem, cang lon cang dat, it may co lon.
DAI = [
    (0, 15, 5_000_000, 13_000_000, 22),
    (15, 20, 7_500_000, 18_000_000, 18),
    (20, 30, 12_000_000, 28_000_000, 12),
    (30, 40, 20_000_000, 40_000_000, 5),
    (40, 60, 30_000_000, 60_000_000, 3),
]

COT = [
    "ma_sp", "ten", "hang", "pham_vi_min", "pham_vi_max", "gia", "gia_goc",
    "do_on_db", "cspf", "sao", "inverter", "lam_lanh_nhanh", "loai_may",
]


def main() -> None:
    rd = random.Random(2026)          # seed co dinh
    rows, stt = [], 0
    for pv_min, pv_max, gia_lo, gia_hi, so_may in DAI:
        for _ in range(so_may):
            stt += 1
            hang = rd.choice(HANG)
            inverter = rd.random() < 0.75
            gia_goc = round(rd.uniform(gia_lo, gia_hi) / 10_000) * 10_000
            # ~35% may dang khuyen mai, giam 5-18%
            gia = (round(gia_goc * (1 - rd.uniform(0.05, 0.18)) / 10_000) * 10_000
                   if rd.random() < 0.35 else gia_goc)
            cspf = round(rd.uniform(4.0, 7.0), 2) if inverter else round(rd.uniform(3.2, 4.8), 2)
            sao = 5.0 if cspf >= 5.5 else (4.0 if cspf >= 4.6 else 3.0)
            do_on = round(rd.uniform(22, 46))

            r = {
                "ma_sp": f"MAU-{stt:03d}",
                "ten": f"{hang} {rd.randint(100, 999)}",
                "hang": hang,
                "pham_vi_min": float(pv_min),
                "pham_vi_max": float(pv_max),
                "gia": gia,
                "gia_goc": gia_goc,
                "do_on_db": do_on,
                "cspf": cspf,
                "sao": sao,
                "inverter": int(inverter),
                "lam_lanh_nhanh": int(rd.random() < 0.5),
                "loai_may": "Máy lạnh 1 chiều (chỉ làm lạnh)",
            }
            rows.append(r)

    # Dong BAN co tinh (~8%): thieu do on / thieu cspf - nhu file that.
    for r in rd.sample(rows, max(1, len(rows) // 12)):
        r[rd.choice(["do_on_db", "cspf"])] = ""

    RA.parent.mkdir(parents=True, exist_ok=True)
    with open(RA, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT)
        w.writeheader()
        w.writerows(rows)
    print(f"Da sinh {len(rows)} may MAU -> {RA}")
    print("Luu y: day la du lieu GIA LAP de repo tu chay duoc - khong phai gia that.")


if __name__ == "__main__":
    main()
