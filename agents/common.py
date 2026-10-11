"""Shared agent helpers."""

from __future__ import annotations

import re
from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def extract_code_block(text: str) -> str:
    if not text:
        return ""
    # If the model emits a tool call write(path=..., content='...'), extract its content
    m_write = re.search(r"\[write\([^)]*?content=(['\"])(.*?)(?:\1\s*\)|$)", text, flags=re.DOTALL)
    if m_write:
        raw_code = m_write.group(2)
        if "\\n" in raw_code:
            try:
                raw_code = raw_code.encode("utf-8").decode("unicode_escape", errors="ignore")
            except Exception:
                raw_code = raw_code.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
        return raw_code.strip()

    text = re.sub(r"<\|tool_call_start\|>.*?<\|tool_call_end\|>", "", text, flags=re.DOTALL)
    text = re.sub(r"<\|tool_call_start\|>.*", "", text, flags=re.DOTALL)
    blocks = re.findall(r"```(?:python)?\s*(.*?)(?:```|$)", text, flags=re.DOTALL | re.IGNORECASE)
    if blocks:
        candidates = [b.strip() for b in blocks if b.strip()]
        if candidates:
            return max(candidates, key=len)
    clean = re.sub(r"^```[a-zA-Z0-9_-]*", "", text).replace("```", "").strip()
    return clean



def normalize_whitespace(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines()).strip() + "\n"
