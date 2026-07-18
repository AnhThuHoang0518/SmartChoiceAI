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
    """FPT AI Marketplace - da doc tai lieu chinh thuc, KHONG doan:
    github.com/fpt-corp/ai-marketplace (README + API Integration - LLM.md)

    Xac nhan tu docs:
      - Base URL : https://mkp-api.fptcloud.com
      - Endpoint : POST /chat/completions  (tuong thich chuan OpenAI)
      - Auth     : header 'Authorization: Bearer <api-key>'
      - Body     : {model, messages[{role,content}], stream}
    Khoa lay o marketplace.fptcloud.com -> My account -> My API Keys.

    json_mode: docs FPT khong nhac response_format -> KHONG gui tham so do
    (server la co the 400). Thay bang chi thi trong system prompt; tang goi
    (trich_o_nhu_cau) von da tu boc ```json``` va tu loai khi sai khuon.
    """

    ten = "fpt"

    def __init__(self, khoa: str, model: str = "DeepSeek-V4-Flash",
                 endpoint: str = "https://mkp-api.fptcloud.com"):
        self._khoa = khoa
        self._model = model
        self._url = (endpoint or "https://mkp-api.fptcloud.com").rstrip("/") + "/chat/completions"

    def sinh(self, he_thong: str, nguoi_dung: str, json_mode: bool = False) -> str:
        import requests

        ht = he_thong + (
            "\nCHỈ trả về JSON hợp lệ, không markdown, không giải thích." if json_mode else ""
        )
        try:
            r = requests.post(
                self._url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._khoa}",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": ht},
                        {"role": "user", "content": nguoi_dung},
                    ],
                    "temperature": 0.2,
                    # max_tokens la tham so chuan OpenAI (API FPT tuong thich OpenAI
                    # theo docs chinh thuc). DeepSeek la model SUY LUAN: no dot
                    # token vao phan "nghi" truoc khi tra loi - dat 500 thi prompt
                    # dai (bang top 3) bi dot sach, content ve RONG (do that tren
                    # may 18/07: cau ngan song, cau tu van chet ca 6/6). 2000 du
                    # cho nghi + 150 tu tra loi; do dai van bi ghim boi luat 150 tu.
                    "max_tokens": 2000,
                    "stream": False,
                },
                timeout=30,
            )
            r.raise_for_status()
            msg = r.json()["choices"][0]["message"]
            text = (msg.get("content") or "").strip()
            if not text:
                # DeepSeek hay viet NGUYEN VAN cau tra loi trong phan suy nghi
                # roi dung (finish=stop, content rong - do that 18/07). Vot doan
                # tra loi khach o cuoi phan nghi; moi con so trong do VAN di qua
                # hau kiem nhu thuong nen khong mo cua cho bia.
                text = self._vot_tu_suy_nghi(msg.get("reasoning_content") or "")
            if not text:
                ly_do = "co reasoning_content (khong vot duoc cau tra loi)" \
                    if msg.get("reasoning_content") else "khong ro ly do"
                raise LoiLLM(f"FPT tra content RONG - {ly_do}; "
                             f"finish={r.json()['choices'][0].get('finish_reason')}")
            return text
        except LoiLLM:
            raise
        except Exception as e:
            raise LoiLLM(f"FPT Marketplace loi: {e}") from e

    @staticmethod
    def _vot_tu_suy_nghi(rc: str) -> str:
        """Tim cau tra loi khach trong phan reasoning cua model suy luan.

        Dau hieu: doan bat dau bang 'Dạ' (giong template minh ep) o vi tri
        muon nhat - model thuong nhap ban cuoi cung ngay truoc khi dung.
        Khong thay thi tra rong -> tang tren roi ve ban du phong.
        """
        import re as _re

        rc = rc.strip()
        if not rc:
            return ""
        vi_tri = max(rc.rfind("\nDạ "), 0 if rc.startswith("Dạ ") else -1)
        if vi_tri >= 0:
            ung = rc[vi_tri:].strip()
        else:
            # Khong co 'Dạ' - vot doan CUOI trong giong tra loi khach: co 'ạ'
            # (prompt ep ket cau bang 'ạ') va du dai. Van qua hau kiem sau.
            ung = ""
            for doan in reversed([d.strip() for d in rc.split("\n\n") if d.strip()]):
                if "ạ" in doan and len(doan) >= 40 and "anh chị" in doan.lower() or \
                        ("ạ." in doan and len(doan) >= 60):
                    ung = doan
                    break
            if not ung:
                return ""
        # cat phan meta neu model con lam nham sau ban nhap
        ung = _re.split(r"\n(?:Wait|Let me|Hmm|Okay|OK,|Actually)\b", ung)[0].strip()
        # qua ngan (< 40 ky tu) thi kho la cau tu van that
        return ung if len(ung) >= 40 else ""


def nhin_anh(khoa: str, anh_b64: str, dinh_dang: str = "jpeg",
             model: str = "Qwen2.5-VL-7B-Instruct") -> str:
    """Qwen2.5-VL doc anh khach chup - theo DUNG docs FPT (VLM.md): OpenAI compat,
    POST /chat/completions, content co type image_url voi data URI base64.

    Prompt ep model CHI mo ta thu NHIN THAY (nhan nang luong, may cu, model) -
    khong doan. Ket qua la van ban tieng Viet, se di vao pipeline trich o nhu
    cau + hau kiem nhu 1 tin nhan khach go tay -> anh khong mo cua cho bia.
    """
    import requests

    ht = ("Bạn là trợ lý điện máy. Nhìn ảnh và cho biết NGẮN GỌN (1-2 câu tiếng Việt): "
          "đây là sản phẩm hay nhãn gì (máy lạnh, tủ lạnh...), hãng, model, và các "
          "thông số ĐỌC ĐƯỢC trên ảnh (HP, dung tích, số sao năng lượng, loại). "
          "CHỈ nói điều nhìn thấy rõ, KHÔNG đoán. Nếu ảnh không phải đồ điện máy, "
          "nói 'Ảnh này không phải sản phẩm điện máy'.")
    try:
        r = requests.post(
            "https://mkp-api.fptcloud.com/chat/completions",
            headers={"Authorization": f"Bearer {khoa}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": ht},
                    {"role": "user", "content": [
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/{dinh_dang};base64,{anh_b64}"}},
                        {"type": "text", "text": "Đây là gì, đọc giúp thông số?"},
                    ]},
                ],
                "temperature": 0.0,
                "max_tokens": 300,
                "stream": False,
            },
            timeout=25,
        )
        r.raise_for_status()
        return (r.json()["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        raise LoiLLM(f"VLM loi: {e}") from e


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
