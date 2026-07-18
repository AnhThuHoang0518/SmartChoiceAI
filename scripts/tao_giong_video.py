"""Sinh giong doc (voice-over) cho video demo bang FPT.AI-VITs, thay nguoi that doc.

Doc tung doan loi thoai (dong bat dau bang "> ") trong docs/video-script.md,
tach nho <=400 ky tu/lan goi (dung nguyen tac giong het backend/app/api/chat.py
- endpoint /api/doc, KHONG bia them tham so API), goi FPT TTS tung doan, roi
noi bang module `wave` co san trong Python (KHONG can cai ffmpeg) thanh 1 file
.wav rieng cho tung doan + 1 file gop toan bo.

Yeu cau: .env co LLM_NHA_CUNG_CAP=fpt va LLM_API_KEY (dung file da co san trong
repo, KHONG commit ket qua .env di dau). Chi verify duoc giong mac dinh
std_kimngan (dung nhu TTS_GIONG trong .env/AGENTS.md) - neu doi giong khac,
tra API Reference tren marketplace.fptcloud.com (can dang nhap) truoc, khong
doan ten giong.

Chay:
    python scripts/tao_giong_video.py
    python scripts/tao_giong_video.py --voice std_kimngan --out docs/video-audio

Ket qua: docs/video-audio/01.wav, 02.wav, ... theo dung thu tu trong kich ban,
va video-audio/full.wav noi het lai (co khoang lang 0.35s giua cac doan).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import wave
from pathlib import Path

import requests
from dotenv import load_dotenv

GIOI_HAN_KY_TU = 400  # dung gioi han trong /api/doc (chi phi + khong chay lan)
FPT_TTS_URL = "https://mkp-api.fptcloud.com/audio/speech"


def doc_doan_thoai(md_path: Path) -> list[str]:
    """Lay cac doan '> ...' trong file md, giu nguyen thu tu xuat hien."""
    text = md_path.read_text(encoding="utf-8")
    doan_hien_tai: list[str] = []
    ket_qua: list[str] = []
    for dong in text.splitlines():
        if dong.startswith("> "):
            doan_hien_tai.append(dong[2:].strip())
        else:
            if doan_hien_tai:
                ket_qua.append(" ".join(doan_hien_tai).strip())
                doan_hien_tai = []
    if doan_hien_tai:
        ket_qua.append(" ".join(doan_hien_tai).strip())
    # Bo doan huong dan quay (khong phai loi thoai) - doan dau file la ghi chu
    # "Quay mot lan lien tuc..." - loai bo neu khong ket thuc bang dau cau
    # thoai thuong (giu don gian: loai doan bat dau bang "Quay " hoac "Dung quay")
    ket_qua = [
        d for d in ket_qua
        if d and not d.lower().startswith(("quay ", "dừng quay"))
    ]
    return ket_qua


def tach_cau(doan: str) -> list[str]:
    """Tach doan thanh cac cau (._!_?_—) de ghep chunk <=400 ky tu ma khong cat ngang cau."""
    # Giu dau cau lai vao cuoi moi cau
    cau_list = re.split(r"(?<=[.!?])\s+", doan.strip())
    return [c.strip() for c in cau_list if c.strip()]


def chia_chunk(doan: str, gioi_han: int = GIOI_HAN_KY_TU) -> list[str]:
    """Gop cac cau lien tiep thanh chunk <=gioi_han ky tu, khong cat ngang cau.
    Neu 1 cau don le da > gioi_han (hiem), buoc phai cat cung theo tu."""
    cau_list = tach_cau(doan)
    chunks: list[str] = []
    hien_tai = ""
    for cau in cau_list:
        ung_vien = (hien_tai + " " + cau).strip() if hien_tai else cau
        if len(ung_vien) <= gioi_han:
            hien_tai = ung_vien
        else:
            if hien_tai:
                chunks.append(hien_tai)
            if len(cau) <= gioi_han:
                hien_tai = cau
            else:
                # cau qua dai - cat theo tu, khong cat ngang API cho phep
                tu_list = cau.split(" ")
                buf = ""
                for tu in tu_list:
                    thu = (buf + " " + tu).strip() if buf else tu
                    if len(thu) <= gioi_han:
                        buf = thu
                    else:
                        chunks.append(buf)
                        buf = tu
                hien_tai = buf
    if hien_tai:
        chunks.append(hien_tai)
    return chunks


def goi_tts(text: str, khoa: str, model: str, voice: str) -> bytes:
    r = requests.post(
        FPT_TTS_URL,
        headers={"Authorization": f"Bearer {khoa}"},
        json={
            "model": model,
            "input": text,
            "response_format": "wav",
            "voice": voice,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.content


def noi_wav(danh_sach_file: list[Path], file_dich: Path, khoang_lang: float = 0.0) -> None:
    """Noi nhieu file wav lai bang module `wave` chuan cua Python (khong can ffmpeg).
    khoang_lang > 0: chen 1 doan lang giua cac file (dung khi noi ca video).
    Gia dinh moi file cung dinh dang (dung API tra ve) - bao loi ro neu lech."""
    params_list = []
    frames_list = []
    for f in danh_sach_file:
        with wave.open(str(f), "rb") as w:
            params_list.append(w.getparams())
            frames_list.append(w.readframes(w.getnframes()))

    goc = params_list[0]
    for f, p in zip(danh_sach_file, params_list):
        if (p.nchannels, p.sampwidth, p.framerate) != (goc.nchannels, goc.sampwidth, goc.framerate):
            raise ValueError(
                f"{f} khac dinh dang audio voi file dau ({p} != {goc}) - khong the noi truc tiep"
            )

    khoang_lang_bytes = b""
    if khoang_lang > 0:
        so_mau = int(goc.framerate * khoang_lang)
        khoang_lang_bytes = b"\x00" * (so_mau * goc.sampwidth * goc.nchannels)

    phan_noi = []
    for i, frames in enumerate(frames_list):
        phan_noi.append(frames)
        if khoang_lang > 0 and i != len(frames_list) - 1:
            phan_noi.append(khoang_lang_bytes)

    with wave.open(str(file_dich), "wb") as w:
        w.setparams(goc)
        w.writeframes(b"".join(phan_noi))


def lay_thoi_luong(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as w:
        return w.getnframes() / w.getframerate()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--md", default="docs/video-script.md", help="File kich ban")
    ap.add_argument("--out", default="docs/video-audio", help="Thu muc luu file audio")
    ap.add_argument("--voice", default=None, help="Ten giong FPT (mac dinh: TTS_GIONG trong .env hoac std_kimngan)")
    ap.add_argument("--model", default=None, help="Ten model FPT (mac dinh: TTS_MODEL trong .env hoac FPT.AI-VITs)")
    args = ap.parse_args()

    load_dotenv()
    nha_cung_cap = (os.getenv("LLM_NHA_CUNG_CAP") or "").strip().lower()
    khoa = (os.getenv("LLM_API_KEY") or "").strip()
    if nha_cung_cap != "fpt" or not khoa:
        print("Loi: .env can LLM_NHA_CUNG_CAP=fpt va LLM_API_KEY (giong backend dung cho /api/doc).", file=sys.stderr)
        return 1

    voice = args.voice or os.getenv("TTS_GIONG", "std_kimngan")
    model = args.model or os.getenv("TTS_MODEL", "FPT.AI-VITs")

    md_path = Path(args.md)
    if not md_path.exists():
        print(f"Loi: khong thay {md_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    doan_list = doc_doan_thoai(md_path)
    if not doan_list:
        print("Khong tim thay doan loi thoai nao (dong bat dau bang '> ') trong file.", file=sys.stderr)
        return 1

    print(f"Tim thay {len(doan_list)} doan loi thoai. Giong: {voice} | Model: {model}\n")

    file_doan: list[Path] = []
    tong_giay = 0.0
    for i, doan in enumerate(doan_list, start=1):
        chunks = chia_chunk(doan)
        print(f"[{i:02d}] {len(doan)} ky tu -> {len(chunks)} chunk")
        chunk_files: list[Path] = []
        for j, chunk in enumerate(chunks, start=1):
            audio = goi_tts(chunk, khoa, model, voice)
            cp = out_dir / f"{i:02d}_{j}.wav"
            cp.write_bytes(audio)
            chunk_files.append(cp)
        dich = out_dir / f"{i:02d}.wav"
        if len(chunk_files) == 1:
            dich.write_bytes(chunk_files[0].read_bytes())
        else:
            noi_wav(chunk_files, dich)
        for cp in chunk_files:
            cp.unlink()
        thoi_luong = lay_thoi_luong(dich)
        tong_giay += thoi_luong
        print(f"     -> {dich.name} ({thoi_luong:.1f}s)")
        file_doan.append(dich)

    full_path = out_dir / "full.wav"
    noi_wav(file_doan, full_path, khoang_lang=0.35)
    thoi_luong_full = lay_thoi_luong(full_path)

    print(f"\nXong: {len(file_doan)} file rieng + {full_path.name}")
    print(f"Tong thoi luong (co khoang lang giua doan): {thoi_luong_full:.1f}s "
          f"({thoi_luong_full/60:.2f} phut)")
    if thoi_luong_full > 180:
        print("CANH BAO: dai hon 3:00 muc tieu cua kich ban 1 shot - can rut loi hoac doc nhanh hon khi quay.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
