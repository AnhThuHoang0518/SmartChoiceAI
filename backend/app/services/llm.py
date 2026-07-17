# -*- coding: utf-8 -*-
"""Adapter LLM - doi nha cung cap bang 1 dong config, khong sua logic.

Vi sao quan trong: de bai ghi ro se TRU DIEM neu "phu thuoc hoan toan vao API
nuoc ngoai khong on dinh hoac qua dat de scale", va tick san "Moi truong trien
khai: On-premise". Kien truc khoa cung vao Gemini la dinh thang cai do.

Co adapter thi:
  - demo chay Gemini (nhanh, da biet chay),
  - va chung minh duoc doi sang model noi dia tren ha tang FPT chi bang 1 dong,
  - khi FPT hong thi bai thi van song.

LLM_NHA_CUNG_CAP=luat  -> khong goi mang. Dung cho CI va khi chua co khoa API:
he thong VAN CHAY duoc het luong, chi kem phan dien dat.
"""
from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod


class LoiLLM(RuntimeError):
    pass


class LLM(ABC):
    ten = "?"

    @abstractmethod
    def sinh(self, he_thong: str, nguoi_dung: str, json_mode: bool = False) -> str:
        ...

    def sinh_do(self, he_thong: str, nguoi_dung: str, json_mode: bool = False):
        """Tra (text, mili_giay). Do thoi gian de doi chieu moc <3s/<5s cua de bai."""
        t0 = time.perf_counter()
        out = self.sinh(he_thong, nguoi_dung, json_mode)
        return out, int((time.perf_counter() - t0) * 1000)


class GeminiLLM(LLM):
    """google-genai (SDK moi). Luu y: timeout trong HttpOptions tinh bang MILI giay,
    khong phai giay - SDK cu tinh bang giay. Dat nham 30 la treo moi request.
    """

    ten = "gemini"

    def __init__(self, khoa: str, model: str = "gemini-2.0-flash"):
        from google import genai

        self._client = genai.Client(api_key=khoa)
        self._model = model

    def sinh(self, he_thong: str, nguoi_dung: str, json_mode: bool = False) -> str:
        from google.genai import types as gt

        cau_hinh = gt.GenerateContentConfig(
            system_instruction=he_thong,
            temperature=0.2,
            response_mime_type="application/json" if json_mode else "text/plain",
        )
        r = self._client.models.generate_content(
            model=self._model, contents=nguoi_dung, config=cau_hinh
        )
        return (r.text or "").strip()


class FptLLM(LLM):
    """FPT AI Factory - Serverless Inference (DeepSeek-V4-Flash, Llama-3.3-70B...).

    CHUA VIET. Ly do: chua co tai lieu chinh thuc trong tay, va luat cua du an la
    KHONG DOAN API (da tra gia mot lan voi SePay). Can xac nhan 3 thu truoc khi
    viet vao day:
      1. Endpoint that (marketplace.fptcloud.jp cho region Nhat - co ban VN khong?)
      2. Kieu xac thuc: 'Authorization: Bearer' hay header rieng?
      3. Body co tuong thich OpenAI (/v1/chat/completions) hay dang rieng?
    Co doc roi thi lop nay chi ~15 dong, khong phai viec lon.
    """

    ten = "fpt"

    def __init__(self, khoa: str, model: str, endpoint: str):
        raise LoiLLM(
            "Driver FPT chua viet - can tai lieu API chinh thuc truoc. "
            "Xem docstring FptLLM de biet can hoi gi. Tam dung LLM_NHA_CUNG_CAP=gemini."
        )

    def sinh(self, he_thong: str, nguoi_dung: str, json_mode: bool = False) -> str:
        raise NotImplementedError


class LuatLLM(LLM):
    """Khong goi mang. Tra ve chuoi rong -> tang tren tu dong roi ve duong luat.

    Day KHONG phai do choi: no la duong lui that. Mat khoa API / het quota /
    FPT sap luc demo -> he thong van hoi nguoc va van xep hang duoc, chi kem
    phan dien dat. Va CI chay duoc ma khong can bi mat nao.
    """

    ten = "luat"

    def sinh(self, he_thong: str, nguoi_dung: str, json_mode: bool = False) -> str:
        return ""


def tao_llm() -> LLM:
    """Doc env. Khong co khoa -> tu ve LuatLLM thay vi no."""
    nha = (os.getenv("LLM_NHA_CUNG_CAP") or "").strip().lower()
    khoa = (os.getenv("LLM_API_KEY") or "").strip()
    model = (os.getenv("LLM_MODEL") or "").strip()

    if nha == "luat" or not khoa:
        return LuatLLM()
    if nha == "fpt":
        return FptLLM(khoa, model or "DeepSeek-V4-Flash", os.getenv("LLM_ENDPOINT", ""))
    return GeminiLLM(khoa, model or "gemini-2.0-flash")
