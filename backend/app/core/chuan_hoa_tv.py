# -*- coding: utf-8 -*-
"""Chuan hoa tieng Viet mua sam THAT truoc khi dua cho LLM trich o nhu cau.

De bai ghi ro phai hieu: "tieng Viet tu nhien, co dau/khong dau, van noi, viet
tat va ngon ngu mua sam pho thong", "co the co loi chinh ta, viet tat, tu dia
phuong, don vi do nhu m2, HP, BTU, GB, lit, inch".

Tang nay la CODE, khong phai LLM. Ly do: viet tat mua sam la tap dong, huu han
va biet truoc -> tra bang vua nhanh (0ms) vua chac. De LLM tu doan '20tr' thi
thinh thoang no ra 20 nghin.

KHONG lam khoi phuc dau tieng Viet day du (can model rieng). Thay vao do:
so khop KHONG DAU - nguoi dung go 'may lanh' hay 'máy lạnh' deu ra cung ket qua.
"""
from __future__ import annotations

import re
import unicodedata

# Viet tat -> day du. Khop tren ban KHONG DAU nen chi can viet khong dau.
VIET_TAT = {
    r"\btk dien\b": "tiết kiệm điện",
    r"\btkd\b": "tiết kiệm điện",
    r"\bdt\b": "diện tích",
    r"\bml\b": "máy lạnh",
    r"\bdhkk\b": "máy lạnh",
    r"\bdieu hoa\b": "máy lạnh",
    r"\bmay lanh\b": "máy lạnh",
    r"\bp ngu\b": "phòng ngủ",
    r"\bpn\b": "phòng ngủ",
    r"\bpk\b": "phòng khách",
    r"\bp khach\b": "phòng khách",
    r"\bit on\b": "ít ồn",
    r"\bem\b(?=\s*(?:hon|nhat))": "êm",
    r"\btra gop\b": "trả góp",
    r"\bkm\b": "khuyến mãi",
    r"\bbh\b": "bảo hành",
    # Tieng Anh pho bien - khach go duoc thi hieu duoc
    r"\bair\s*con(?:ditioner)?\b": "máy lạnh",
    r"\bfridge\b|\brefrigerator\b": "tủ lạnh",
    r"\bwashing\s*machine\b|\bwasher\b": "máy giặt",
}


def bo_dau(s: str) -> str:
    """'máy lạnh' -> 'may lanh'. Dung de SO KHOP, khong dung de hien thi."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", s).replace("đ", "d").replace("Đ", "D")


# So dien thoai la du lieu ca nhan, dong thoi rat de bi regex ngan sach nham
# thanh mot so tien lon (0912345678 -> 912.345.678d). Nhan dien truoc moi
# buoc chuan hoa/trich o; cho phep cach viet co dau cach, cham hoac gach ngang.
_MAU_SO_DIEN_THOAI = re.compile(
    r"(?<!\d)(?:\+?84|0)(?:[\s.\-]*\d){9}(?!\d)"
)


def so_dien_thoai_trong(text: str) -> bool:
    return bool(_MAU_SO_DIEN_THOAI.search(text or ""))


def bo_so_dien_thoai(text: str) -> str:
    """Bo PII khoi van ban dua vao bo trich o, khong tra lai gia tri da bo."""
    return _MAU_SO_DIEN_THOAI.sub(" ", text or "")


def can_hoi_lam_ro_nganh(text: str) -> bool:
    """Cau mua sam noi 'may/san pham' nhung khong co dau hieu rieng may lanh.

    Khong tu mac dinh may lanh cho cac tieu chi dung duoc o nhieu nganh nhu
    tiet kiem dien, chay em hay gia. Van giu luong rut gon cho cau co m2/BTU/HP
    vi day la bang chung ky thuat rieng cua may lanh.
    """
    kd = bo_dau(text or "").lower()
    if not re.search(r"\b(?:may|san pham|thiet bi|cai|con)\b", kd):
        return False
    return not bool(re.search(
        r"\b(?:lam lanh|cong suat lanh|btu|hp|ngua|dieu hoa|may lanh)\b"
        r"|\b\d+(?:[.,]\d+)?\s*m(?:2|²)\b",
        kd,
    ))


def chuan_hoa_tien(s: str) -> str:
    """'20tr' -> '20000000'. '500k' -> '500000'.

    Lam o day chu khong de LLM doan: '20tr' ra '20 nghin' la sai gia 1000 lan,
    ma sai gia la thu de bai cham nang nhat.
    """
    def _tr(m):
        v = float(m.group(1).replace(",", "."))
        return str(int(v * 1_000_000))

    def _k(m):
        v = float(m.group(1).replace(",", "."))
        return str(int(v * 1_000))

    def _ty(m):
        v = float(m.group(1).replace(",", "."))
        return str(int(v * 1_000_000_000))

    # 'X trieu ruoi' -> X.5 trieu (quy doi tieng Viet, chay TRUOC luat trieu)
    s = re.sub(r"\b([\d]+)\s*(?:triệu|trieu|tr)\s*(?:rưỡi|ruoi)\b",
               lambda m: str(int((int(m.group(1)) + 0.5) * 1_000_000)), s, flags=re.I)
    # 'ty/ti' khong dau chi khop khi co SO dung truoc -> khong dinh 'ti vi'.
    # Bai hoc tu demo that: khach go '20 tỷ' ma khong hieu -> hoi ngan sach lap
    # vo tan. Tien VN co 4 don vi noi mieng: nghin/k, trieu/tr, ty - thieu 1 la thua.
    s = re.sub(r"\b([\d.,]+)\s*(?:tỷ|tỉ|ty|ti)\b", _ty, s, flags=re.I)
    s = re.sub(r"\b([\d.,]+)\s*(?:tr|trieu|triệu)\b", _tr, s, flags=re.I)
    s = re.sub(r"\b([\d.,]+)\s*(?:k|nghin|nghìn)\b", _k, s, flags=re.I)
    return s


# ── Nganh hang ngoai pham vi demo ───────────────────────────────────────────
# File du lieu that co 14 nganh, demo moi bat may lanh. Khach hoi nganh khac
# thi phai NOI THANG, khong duoc lai cau hoi ngan sach nhu robot hong.

# 'tu lanh' DA GO khoi danh sach nay: tu 18/07 nganh tu lanh co vertical rieng
# (backend/app/nganh/tu_lanh.py) - router trong api se dan sang, khong tu choi nua.
NGANH_KHAC = [
    # 'may giat' + 'may say' DA GO (18/07): chay tren khung generic configs/nganh/
    (r"\b(?:tivi|ti vi|tv\b)\b", "tivi"),
    (r"\b(?:laptop|may tinh xach tay|macbook)\b", "laptop"),
    # khach hoi ten dong may cu the ('cos iphone 13 k?') cung phai nhan ra
    # nganh dien thoai - bug demo that 19/07: bot chao lai nhu chua nghe
    (r"\b(?:dien thoai|iphone|smartphone|smart phone|dtdd|dth)\b", "điện thoại"),
]


def co_nganh_may_lanh(text: str) -> bool:
    """Khach co nhac toi may lanh khong (ke ca tieng Anh pho bien)."""
    return bool(re.search(r"\b(may lanh|dieu hoa|dhkk|ml|air ?con(?:ditioner)?)\b",
                          bo_dau(text or "").lower()))


def co_nganh_tu_lanh(text: str) -> bool:
    """Khach nhac tu lanh - nganh thu 2 da co vertical rieng."""
    return bool(re.search(r"\btu lanh\b|\bfridge\b|\brefrigerator\b",
                          bo_dau(text or "").lower()))


# ── Suy luan UNG VIEN nganh - chua xac nhan thi KHONG ghi vao nhu cau ──────

def goi_y_may_lanh_tu_nhu_cau_lam_mat(text: str) -> bool:
    """Cau mo ho ve nong + y dinh mua -> CHI goi y may lanh de khach xac nhan.

    Day khong phai router nganh va khong dien bat ky o nhu cau nao. Cac cum ve
    san pham dang nong/hong, nuoc nong, tu lanh... bi loai de khong bien mot
    cau bao loi thanh nhu cau mua may lanh.
    """
    kd = bo_dau(text or "").lower()

    # Nganh/san pham co chu "nong/lanh" nhung khong phai nhu cau lam mat.
    if re.search(r"\b(may nuoc nong|binh nong lanh|tu lanh|fridge|refrigerator)\b", kd):
        return False
    # Bao thiet bi bi nong hoac khong lam lanh = tinh trang/bao loi, khong phai
    # loi moi mua do lam mat.
    if re.search(r"\b(?:dien thoai|laptop|pc|may tinh|pin|sac|dong co|may|tu)\s+(?:bi\s+)?nong\b", kd):
        return False
    if re.search(r"\b(?:may lanh|tu lanh).{0,18}\b(?:khong lanh|khong mat|bi hong|hong)\b", kd):
        return False
    if re.search(r"\b(?:nuoc|do an|thuc an|bep|lo|binh)\s+nong\b", kd):
        return False

    co_nhu_cau_lam_mat = bool(re.search(
        r"\b(nong qua|nong buc|oi buc|oi qua|nuc|nong|oi|giai nong|cho mat|lam mat)\b",
        kd,
    ))
    co_y_dinh_mua = bool(re.search(
        r"\b(mua|chon|tim|can|nen|tu van|goi y|ban|co loai gi|co gi)\b",
        kd,
    ))
    return co_nhu_cau_lam_mat and co_y_dinh_mua


def tra_loi_xac_nhan_goi_y(text: str) -> bool | None:
    """True=dong y, False=tu choi, None=chua tra loi ro cau xac nhan."""
    kd = bo_dau(text or "").lower().strip()
    if re.search(r"\b(khong phai|khong|ko|k|sai|san pham khac|mon khac|cai khac)\b", kd):
        return False
    if re.search(r"\b(dung|dung roi|duoc|dc|ok|oki|uh|u|vang|yes|tim may lanh|mua may lanh)\b", kd):
        return True
    return None


def chi_la_xac_nhan_dong_y(text: str) -> bool:
    """Cau chi co y xac nhan; co them dien tich/tien thi router phai doc tiep."""
    kd = bo_dau(text or "").lower().strip()
    return bool(re.fullmatch(
        r"(?:dung|dung roi|duoc|dc|ok|oki|uh|u|vang|yes|"
        r"dung,? tim may lanh|tim may lanh|mua may lanh)",
        kd,
    ))


# ── Nhan biet khach ranh ky thuat ───────────────────────────────────────────
# Sale that doi giong theo khach: khach binh dan thi noi loi ich, khach ranh
# ky thuat thi noi thang so. Nhan biet qua CHINH ngon ngu khach go - dung
# regex chu khong dung LLM: chac chan, giai trinh duoc, 0ms.

TU_KY_THUAT = (
    "cspf", "btu", "hp", "db", "decibel", "gas r32", "r32", "r410",
    "dan nong", "dan lanh", "2 chieu", "hai chieu", "cong suat lanh",
    "nhan nang luong", "eer", "seer",
)


def tu_ky_thuat_trong(text: str) -> set[str]:
    """Tap thuat ngu ky thuat xuat hien trong cau. Cong don qua ca phien:
    >=2 thuat ngu khac nhau -> khach ranh ky thuat."""
    kd = bo_dau(text or "").lower()
    return {t for t in TU_KY_THUAT if re.search(rf"\b{re.escape(t)}\b", kd)}


def yeu_cau_thong_so(text: str) -> bool:
    """Khach chu dong doi xem thong so ('cho xin thong so chi tiet') - chuyen
    giong ky thuat ngay, khoi cho du 2 thuat ngu."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(r"\b(thong so (chi tiet|day du|ky thuat)|chi tiet thong so|"
                          r"xin thong so|noi thong so|spec)\b", kd))


def bo_ngan_sach(text: str) -> bool:
    """Khach tuyen bo KHONG quan tam tien nua ('ko can quan tam ngan sach',
    'bao nhieu cung duoc', 'toi se tra dung gia'). Bug demo that: khach noi vay
    ma bot van lai 'trong tam 20 trieu em chua tim duoc...' y het - vi khong co
    duong nao xoa/noi ngan sach da chot."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(
        r"(?:(?:khong|ko|k) (?:can )?quan tam.{0,15}(?:ngan sach|tien|gia)"
        r"|(?:ngan sach|tien|gia).{0,10}(?:khong|ko) (?:quan trong|thanh van de)"
        r"|bao nhieu (?:tien )?cung (?:duoc|dc|ok)"
        r"|gia nao cung (?:duoc|dc|ok)"
        r"|khong gioi han(?: ngan sach| tien)?"
        r"|bo (?:gioi han|ngan sach)"
        r"|tra dung gia)",
        kd,
    ))


def hoi_ton_kho(text: str) -> bool:
    """Khach hoi con hang/ton kho/chi nhanh. Du lieu hien KHONG co ton kho -
    phai NOI THANG thieu nguon va can Stock API (test case TC-008/TC-017:
    'khong suy doan tu kien thuc nen'), khong duoc im lang bo qua."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(
        r"\b(con hang|ton kho|het hang|hang co san|chi nhanh|cua hang nao|"
        r"o dau (?:co|ban)|ship (?:ve|den)|giao (?:ve|den))\b", kd))


def hoi_chu_quan(text: str) -> str | None:
    """Khach hoi tieu chi CHU QUAN hoac thu du lieu khong do duoc: 'dep nhat',
    'sang nhat', 'ben nhat'. Test case TC-009/TC-025: phai neu ro day la tieu
    chi chu quan / khong co truong du lieu, KHONG xep hang bua.
    Tra ve ten tieu chi de dien vao template, None neu khong dinh."""
    kd = bo_dau(text or "").lower()
    for mau, ten in [
        (r"\b(dep|sang|xin|thoi trang|ngau) (?:nhat|hon|nao)\b", "đẹp/sang"),
        (r"\bmau (?:nao )?dep\b", "đẹp/sang"),
        (r"\b(ben|ben bi) (?:nhat|hon|khong|nao)\b", "độ bền"),
        # CHU Y khong dua 'tot nhat/ngon nhat' vao day: do la cau mo mang mo ho
        # binh thuong - sale dap bang cach GOM NHU CAU (flow hien tai da dung),
        # khong phai bai giang ve tinh chu quan.
    ]:
        if re.search(mau, kd):
            return ten
    return None


def hoi_khuyen_mai(text: str) -> bool:
    """Khach hoi may dang giam gia/khuyen mai. Tra loi bang du lieu THAT
    (gia goc vs gia khuyen mai co san trong catalog) - khong doan 'hot',
    khong doan 'noi bat' vi khong co so lieu nao dung sau mot chu do."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(r"\b(khuyen mai|giam gia|dang giam|dang sale|sale|km)\b", kd))


def cau_hoi_cong_suat(text: str) -> bool:
    """Khach hoi KIEN THUC ve cong suat ('gia dinh 5 nguoi mua cong suat bao
    nhieu?', 'phong nay can may HP?') - khac voi nho tu van chon may.

    Phat hien tu demo that: he chi co 2 che do (hoi nguoc / top 3) nen cau hoi
    kien thuc bi tra loi bang... nguyen van cau tu van cu. Can che do thu 3:
    GIAI THICH - template co can cu, khong qua LLM.
    """
    kd = bo_dau(text or "").lower()
    if not re.search(r"\b(cong suat|hp|btu|ngua)\b", kd):
        return False
    return bool(re.search(r"\b(bao nhieu|bn|nao|the nao|sao|can|nen|du)\b", kd))


# Tu tieng Viet pho thong hay xuat hien trong TEN HANG ("Hoa Phat") - khong
# duoc dung mot minh de nhan hang, vi "dieu hoa" se dinh "Hoa Phat" (bug that).
_TU_MO_HO = {"hoa", "phat", "viet", "nam", "thai", "hong", "quoc", "tan", "dai",
             "son", "minh", "thanh", "xuan", "gia", "may", "dien"}


def trich_hang(text: str, cac_hang: set[str]) -> str | None:
    """Tim ten HANG trong cau khach - doi chieu danh sach hang THAT cua catalog
    (khong co danh sach hang tu che). Tra ten hang dung chinh ta cua catalog.

    Luat khop, tu chat den long:
      1. Nguyen cum ten hang ("hoa phat", "ipad (apple)" -> "ipad apple")
      2. Tung tu trong ten hang, tu >=4 ky tu va KHONG phai tu tieng Viet mo ho
         ("apple" trong "Ipad (Apple)" - khach go 'apple' van ra)
      3. Hang ten ngan 1 tu (LG, TCL): khop nguyen tu
    """
    kd = bo_dau(text or "").lower()

    def _co(cum: str) -> bool:
        return bool(cum) and bool(
            re.search(rf"(?<![a-z0-9]){re.escape(cum)}(?![a-z0-9])", kd))

    ung_vien = []                          # (do dai khop, ten hang goc)
    for h in cac_hang:
        if not h:
            continue
        hb = re.sub(r"[^a-z0-9]+", " ", bo_dau(h).lower()).strip()
        tu_cua_hang = hb.split()
        if _co(hb):                                        # 1. nguyen cum
            ung_vien.append((len(hb), h))
            continue
        for tu in tu_cua_hang:
            du_dai = len(tu) >= 4 and tu not in _TU_MO_HO  # 2. tu dai ro nghia
            ten_ngan = len(tu_cua_hang) == 1               # 3. LG / TCL
            if (du_dai or ten_ngan) and _co(tu):
                ung_vien.append((len(tu), h))
                break
    return max(ung_vien)[1] if ung_vien else None


def bo_hang(text: str) -> bool:
    """Khach tuyen bo khong quan trong hang -> xoa loc hang dang co."""
    kd = bo_dau(text or "").lower()
    return bool(re.search(
        r"hang nao cung (?:duoc|dc|ok)|(?:khong|ko) quan trong hang|hang gi cung duoc"
        r"|bo (?:loc )?hang|khong can hang", kd))


def hoi_hang(text: str) -> bool:
    """Khach hoi CO NHUNG HANG NAO - tra loi bang danh sach hang that trong
    catalog nganh (dem duoc), khong ke ten hang ngoai du lieu."""
    kd = bo_dau(text or "").lower()
    if bo_hang(text):
        return False
    return bool(re.search(
        r"(?:nhung|co|ban) (?:hang|thuong hieu) (?:nao|gi)|hang nao (?:tot|ngon|ok|uy tin)"
        r"|(?:hang|thuong hieu) nao dang|cac hang nao|nhung thuong hieu nao", kd))


def hoi_vi_sao_xep(text: str) -> int | None:
    """Khach hoi VI SAO de xuat/xep hang: 'sao lai chon may 1?', 'vi sao may
    nay dung dau?'. Tra chi so may (mac dinh 0 = may dau bang).

    Tra loi bang BANG DIEM code da tinh - he giai trinh duoc chinh minh,
    khong nho LLM bao chua.
    """
    kd = bo_dau(text or "").lower()
    if not re.search(r"\b(?:vi sao|tai sao|sao lai|ly do(?: gi| nao)?)\b.{0,30}"
                     r"\b(?:chon|xep|de xuat|goi y|dung dau|so 1|may nay|may \d)\b", kd):
        return None
    m = re.search(r"may\s*(?:so\s*)?([123])\b", kd)
    return int(m.group(1)) - 1 if m else 0


def yeu_cau_so_sanh(text: str) -> tuple[int, int] | None:
    """Khach xin SO SANH truc tiep 2 may trong top 3 vua tu van.

    'so sánh máy 1 và máy 2' -> (0, 1) | 'so sánh máy 1 với 3' -> (0, 2)
    'so sánh 2 máy đầu' / 'so sánh đi' -> (0, 1) mặc định.
    Chi tra chi so - viec co top 3 de so hay khong do router quyet.
    """
    kd = bo_dau(text or "").lower()
    if not re.search(r"\bso sanh\b", kd):
        return None
    # bat cap chi so ro rang truoc ('may 1 va may 3'); '2 may dau' khong tinh
    so = [int(x) for x in re.findall(r"(?:may|tu|cai|san pham|sp|so|thu)\s*([123])\b", kd)]
    if len(so) >= 2 and so[0] != so[1]:
        return so[0] - 1, so[1] - 1
    return 0, 1


def muc_gia(text: str) -> str | None:
    """Khach noi TAM GIA thay vi con so: 'tầm trung', 'giá rẻ thôi', 'cao cấp'.

    Chi tra nhan muc - nguong tien cu the do code tinh tu PHAN BO GIA THAT cua
    catalog nganh do (tercile), khong bia nguong. Co y KHONG bat chu 're' tran
    (do la uu tien gia, da co duong rieng) - chi bat khi khach ro rang noi ve
    tam gia."""
    kd = bo_dau(text or "").lower()
    if re.search(r"\btam trung\b|\btam gia trung\b|gia trung binh", kd):
        return "trung"
    if re.search(r"\b(gia re thoi|re nhat co the|loai re|hang binh dan|phan khuc re|cang re cang tot)\b", kd):
        return "re"
    if re.search(r"\b(cao cap|hang xin|phan khuc cao|flagship)\b", kd):
        return "cao"
    return None


def nganh_ngoai_pham_vi(text: str) -> str | None:
    """Khach dang hoi nganh khac (khong nhac may lanh) -> tra ten nganh do.

    Co nhac may lanh thi coi nhu dung pham vi (vd 'mua may lanh va tu lanh'
    -> van tu van may lanh, nganh kia tu nhien duoc nhac trong cau tra loi).
    """
    kd = bo_dau(text or "").lower()
    if re.search(r"\b(may lanh|dieu hoa|dhkk|ml)\b", kd):
        return None
    for mau, ten in NGANH_KHAC:
        if re.search(mau, kd):
            return ten
    return None


def chuan_hoa_don_vi(s: str) -> str:
    """'18m2', '18 met vuong', '18m^2' -> '18m²'."""
    return re.sub(r"\b(\d+(?:[.,]\d+)?)\s*(?:m2|m\^2|m²|met vuong|mét vuông)\b",
                  r"\1m²", s, flags=re.I)


def chuan_hoa(s: str) -> str:
    """Ham chinh: van ban tho -> van ban da chuan hoa cho LLM trich o nhu cau."""
    goc = (s or "").strip()
    if not goc:
        return ""

    # Mo viet tat: khop tren ban khong dau, thay tren ban goc theo vi tri.
    khong_dau = bo_dau(goc).lower()
    thay: list[tuple[int, int, str]] = []
    for mau, day_du in VIET_TAT.items():
        for m in re.finditer(mau, khong_dau):
            thay.append((m.start(), m.end(), day_du))
    thay.sort(key=lambda x: -x[0])          # thay tu cuoi len de khong lech vi tri
    ra = goc
    for i, j, day_du in thay:
        ra = ra[:i] + day_du + ra[j:]

    return chuan_hoa_don_vi(chuan_hoa_tien(ra))


def dem_nguoi(text: str) -> int | None:
    """'2 vo chong 2 dua con' -> 4 | 'vo chong va 1 be' -> 3.

    PHEP DEM tu loi khach, khong doan. Khach da noi thang 'X nguoi' thi khong
    can (duong trich truc tiep lo roi). Khong thay thanh phan nao -> None.
    """
    kd = bo_dau(text or "").lower()
    if re.search(r"\d\s*nguoi\b(?!\s*lon)", kd):
        return None                        # da co so truc tiep ('4 nguoi') - khong dem de
    tong = 0
    if re.search(r"\b(?:2\s*)?vo chong\b|\b2\s*vc\b|\bhai vo chong\b", kd):
        tong += 2
    if m := re.search(r"(\d)\s*nguoi lon", kd):
        tong += int(m.group(1))
    if m := re.search(r"(\d)\s*(?:dua con|tre em|tre nho|con nho|dua tre|em be|be con|dua nho)", kd):
        tong += int(m.group(1))
    elif re.search(r"\bmot (?:dua con|be|chau)\b|\b1 (?:be|chau)\b", kd):
        tong += 1
    return tong or None
