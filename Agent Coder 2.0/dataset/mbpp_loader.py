"""MBPP dataset loading with explicit generation/evaluation separation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from datasets import load_dataset


@dataclass(frozen=True)
class MBPPProblem:
    task_id: int
    text: str
    entry_point: str | None = None
    test_setup_code: str | None = None
    code: str | None = None
    test_list: list[str] | None = None
    challenge_test_list: list[str] | None = None

    def generation_view(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "text": self.text,
            "entry_point": self.entry_point,
        }

    def evaluation_view(self) -> dict[str, Any]:
        return asdict(self)


def _extract_entry_point(raw: dict[str, Any]) -> str | None:
    if raw.get("entry_point"):
        return str(raw["entry_point"])
    import re
    for test in raw.get("test_list") or []:
        m = re.search(r"assert\s+([a-zA-Z_]\w*)\s*\(", test)
        if m:
            return m.group(1)
    code = raw.get("code") or ""
    m = re.search(r"def\s+([a-zA-Z_]\w*)\s*\(", code)
    if m:
        return m.group(1)
    return None


def _from_raw(raw: dict[str, Any]) -> MBPPProblem:
    test_setup = raw.get("test_setup_code")
    if not test_setup and raw.get("test_imports"):
        test_setup = "\n".join(raw["test_imports"])
    return MBPPProblem(
        task_id=int(raw.get("task_id", raw.get("id", 0))),
        text=str(raw.get("text", raw.get("prompt", ""))).strip(),
        entry_point=_extract_entry_point(raw),
        test_setup_code=test_setup,
        code=raw.get("code"),
        test_list=list(raw.get("test_list", [])) if raw.get("test_list") is not None else None,
        challenge_test_list=list(raw.get("challenge_test_list", []))
        if raw.get("challenge_test_list") is not None
        else None,
    )



def load_mbpp(
    *,
    split: str = "test",
    name: str = "sanitized",
    limit: int | None = None,
    start: int | None = None,
    end: int | None = None,
    task_id: int | None = None,
    local_path: str | None = None,
) -> list[MBPPProblem]:
    if local_path:
        raw_items = json.loads(Path(local_path).read_text(encoding="utf-8"))
    else:
        raw_items = list(load_dataset("mbpp", name=name, split=split))

    problems = [_from_raw(dict(item)) for item in raw_items]

    if task_id is not None:
        problems = [problem for problem in problems if problem.task_id == task_id]
    if start is not None:
        problems = problems[start:]
    if end is not None:
        problems = problems[: end if start is None else end - (start or 0)]
    if limit is not None:
        problems = problems[:limit]
    return problems


def sanitize_for_generation(problem: MBPPProblem) -> dict[str, Any]:
    """Return the exact generation payload. Reference solution and tests are excluded."""

    return problem.generation_view()


def evaluation_payload(problem: MBPPProblem) -> dict[str, Any]:
    """Return the full record for evaluation-only use."""

    return problem.evaluation_view()
