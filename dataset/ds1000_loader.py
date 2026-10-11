"""DS-1000 dataset loader with strict isolation of reference code and test contexts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from datasets import load_dataset


@dataclass(frozen=True)
class DS1000Problem:
    task_id: int
    prompt: str
    code_context: str
    lib: str
    reference_code: str | None = None
    entry_point: str | None = "solution"

    @property
    def text(self) -> str:
        return self.prompt

    def generation_view(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "lib": self.lib,
            "entry_point": self.entry_point,
        }

    def evaluation_view(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_lib_name(name: str) -> str:
    cleaned = name.lower().replace("-", "").replace("_", "")
    if cleaned in ("sklearn", "scikitlearn"):
        return "sklearn"
    if cleaned in ("tensorflow", "tf"):
        return "tensorflow"
    if cleaned in ("matplotlib", "plt"):
        return "matplotlib"
    if cleaned in ("pytorch", "torch"):
        return "pytorch"
    return cleaned


def _from_raw(raw: dict[str, Any], idx: int) -> DS1000Problem:
    meta = raw.get("metadata") or {}
    task_id = int(raw.get("problem_id", meta.get("problem_id", raw.get("task_id", idx))))
    prompt = str(raw.get("prompt", "")).strip()
    code_context = str(raw.get("code_context", "")).strip()
    lib = str(raw.get("lib", meta.get("library", raw.get("library", "Unknown")))).strip()
    reference_code = raw.get("reference_code")

    return DS1000Problem(
        task_id=task_id,
        prompt=prompt,
        code_context=code_context,
        lib=lib,
        reference_code=reference_code,
        entry_point="solution",
    )


def load_ds1000(
    *,
    split: str = "test",
    limit: int | None = None,
    start: int | None = None,
    end: int | None = None,
    task_id: int | None = None,
    lib: str | None = None,
    local_path: str | None = None,
) -> list[DS1000Problem]:
    """Load DS-1000 dataset items."""
    if local_path and Path(local_path).exists():
        raw_items = json.loads(Path(local_path).read_text(encoding="utf-8"))
        if isinstance(raw_items, dict) and "data" in raw_items:
            raw_items = raw_items["data"]
    else:
        try:
            ds = load_dataset("xlangai/DS-1000", split=split)
            raw_items = [dict(item) for item in ds]
        except Exception:
            # Fallback if offline or HuggingFace requires local cache
            raw_items = []

    problems: list[DS1000Problem] = []
    for idx, item in enumerate(raw_items):
        problem = _from_raw(item, idx)
        if lib and _normalize_lib_name(problem.lib) != _normalize_lib_name(lib):
            continue
        problems.append(problem)

    if task_id is not None:
        problems = [p for p in problems if p.task_id == task_id]
    if start is not None:
        problems = problems[start:]
    if end is not None:
        problems = problems[: end if start is None else end - (start or 0)]
    if limit is not None:
        problems = problems[:limit]

    return problems
