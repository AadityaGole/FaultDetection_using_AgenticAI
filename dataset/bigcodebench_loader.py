"""BigCodeBench-Instruct dataset loading and sanitation helpers."""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from datasets import load_dataset


def _parse_jsonish(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            return json.loads(text)
        except Exception:
            try:
                return ast.literal_eval(text)
            except Exception:
                return value
    return value


@dataclass(frozen=True)
class BigCodeBenchProblem:
    task_id: str
    instruct_prompt: str
    complete_prompt: str
    code_prompt: str
    canonical_solution: str
    test: str
    entry_point: str = "task_func"
    doc_struct: dict[str, Any] | None = None
    libs: list[str] | None = None

    @property
    def text(self) -> str:
        return self.instruct_prompt

    @property
    def prompt(self) -> str:
        return self.instruct_prompt

    def generation_view(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "instruct_prompt": self.instruct_prompt,
            "entry_point": self.entry_point,
            "libs": self.libs or [],
        }

    def evaluation_view(self) -> dict[str, Any]:
        return asdict(self)


def _from_raw(raw: dict[str, Any], idx: int) -> BigCodeBenchProblem:
    doc_struct = _parse_jsonish(raw.get("doc_struct"), {})
    libs = _parse_jsonish(raw.get("libs"), [])
    if isinstance(libs, str):
        libs = [libs]
    if not isinstance(doc_struct, dict):
        doc_struct = {"raw": doc_struct}
    if not isinstance(libs, list):
        libs = [str(libs)]

    return BigCodeBenchProblem(
        task_id=str(raw.get("task_id", f"BigCodeBench/{idx}")),
        instruct_prompt=str(raw.get("instruct_prompt", raw.get("complete_prompt", raw.get("code_prompt", "")))).strip(),
        complete_prompt=str(raw.get("complete_prompt", "")).strip(),
        code_prompt=str(raw.get("code_prompt", "")).strip(),
        canonical_solution=str(raw.get("canonical_solution", "")).strip(),
        test=str(raw.get("test", "")).strip(),
        entry_point=str(raw.get("entry_point", "task_func")).strip() or "task_func",
        doc_struct=doc_struct,
        libs=[str(item) for item in libs],
    )


def load_bigcodebench(
    *,
    split: str = "v0.1.4",
    limit: int | None = None,
    start: int | None = None,
    end: int | None = None,
    task_id: str | None = None,
    local_path: str | None = None,
) -> list[BigCodeBenchProblem]:
    """Load BigCodeBench-Instruct tasks."""
    if local_path and Path(local_path).exists():
        raw_items = json.loads(Path(local_path).read_text(encoding="utf-8"))
        if isinstance(raw_items, dict) and "data" in raw_items:
            raw_items = raw_items["data"]
    else:
        ds = load_dataset("bigcode/bigcodebench", split=split)
        raw_items = [dict(item) for item in ds]

    problems = [_from_raw(dict(item), idx) for idx, item in enumerate(raw_items)]

    if task_id is not None:
        problems = [problem for problem in problems if str(problem.task_id) == str(task_id)]
    if start is not None:
        problems = problems[start:]
    if end is not None:
        problems = problems[: end if start is None else end - (start or 0)]
    if limit is not None:
        problems = problems[:limit]
    return problems
