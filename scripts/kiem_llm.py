# -*- coding: utf-8 -*-
"""Goi LLM THAT 1 phat duy nhat, in loi NGUYEN VAN - de biet vi sao LLM chet.

Chay:  python scripts/kiem_llm.py
"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import os  # noqa: E402

print("LLM_NHA_CUNG_CAP =", os.getenv("LLM_NHA_CUNG_CAP", "(chua dat - mac dinh)"))
print("Co LLM_API_KEY   =", bool(os.getenv("LLM_API_KEY")))
print("LLM_MODEL        =", os.getenv("LLM_MODEL", "(mac dinh cua adapter)"))

from backend.app.services.llm import tao_llm  # noqa: E402

llm = tao_llm()
print("Adapter dang dung:", llm.ten)

t0 = time.perf_counter()
try:
    text, ms = llm.sinh_do(
        "Bạn là trợ lý. Trả lời đúng 1 câu tiếng Việt.",
        "Chào bạn, hôm nay thế nào?",
    )
    print(f"\nOK sau {time.perf_counter() - t0:.1f}s (ms noi bo: {ms})")
    print("Tra loi:", (text or "(RONG)")[:200])
except Exception:  # noqa: BLE001
    print(f"\nLOI sau {time.perf_counter() - t0:.1f}s:")
    traceback.print_exc()
