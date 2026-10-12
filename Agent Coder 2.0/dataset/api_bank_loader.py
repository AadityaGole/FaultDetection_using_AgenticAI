"""API-Bank dataset loader supporting Level 1 and Level 2 dialogue turns."""

from __future__ import annotations

import ast
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from datasets import load_dataset


def api_bank_cache_dir() -> Path:
    from huggingface_hub.constants import HF_HUB_CACHE

    return Path(os.environ.get("HF_HUB_CACHE", str(HF_HUB_CACHE))).expanduser()


def _cached_api_bank_file(level: int) -> Path | None:
    cache_root = api_bank_cache_dir()
    snapshot_root = cache_root / "datasets--liminghao1630--API-Bank" / "snapshots"
    candidates = list(snapshot_root.glob(f"*/test-data/level-{level}-api.json"))
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


@dataclass(frozen=True)
class APIBankTurn:
    task_id: int | str
    level: int
    dialogue_id: str
    turn_id: int
    api_descriptions: str
    dialogue_history: list[dict[str, Any]]
    expected_api_name: str
    expected_param_dict: dict[str, Any]
    prompt: str

    @property
    def text(self) -> str:
        return self.prompt

    @property
    def entry_point(self) -> str:
        return self.expected_api_name

    def generation_view(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "level": self.level,
            "dialogue_id": self.dialogue_id,
            "turn_id": self.turn_id,
            "prompt": self.prompt,
        }

    def evaluation_view(self) -> dict[str, Any]:
        return asdict(self)


def format_api_bank_prompt(api_descriptions: str, history: list[dict[str, Any]]) -> str:
    history_text = []
    for item in history:
        role = item.get("role", "User")
        text = item.get("text", "")
        if role == "API":
            params = ", ".join(f"{k}={v!r}" for k, v in item.get("param_dict", {}).items())
            history_text.append(f"API: [{item.get('api_name')}({params})] Response: {item.get('result', '')}")
        else:
            history_text.append(f"{role}: {text}")

    dialogue_str = "\n".join(history_text)
    return (
        "You are an API calling assistant.\n"
        "Given the available API documentation and conversation history, determine the exact API call required.\n\n"
        f"Available APIs:\n{api_descriptions}\n\n"
        f"Conversation History:\n{dialogue_str}\n\n"
        "Instruction: Output ONLY the API call in the format: [ApiName(param1='value1', param2='value2')]. "
        "Do not include explanation or additional text."
    )


def load_api_bank(
    *,
    level: int = 1,
    split: str = "test",
    limit: int | None = None,
    start: int | None = None,
    end: int | None = None,
    task_id: int | str | None = None,
    local_path: str | None = None,
) -> list[APIBankTurn]:
    """Load API-Bank dialogue turns."""
    from evaluation.api_bank_evaluator import parse_api_call

    raw_samples: list[dict[str, Any]] = []

    if local_path:
        path = Path(local_path)
        if not path.is_file():
            raise FileNotFoundError(f"API-Bank local dataset file does not exist: {path}")
        raw_data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw_data, list):
            raw_samples = raw_data
        elif isinstance(raw_data, dict) and "turns" in raw_data:
            raw_samples = raw_data["turns"]
    else:
        cached_file = _cached_api_bank_file(level)
        if cached_file is not None:
            raw_samples = json.loads(cached_file.read_text(encoding="utf-8"))
        else:
            try:
                ds = load_dataset(
                    "liminghao1630/API-Bank",
                    data_files={"test": f"test-data/level-{level}-api.json"},
                )
                raw_samples = [dict(item) for item in ds["test"]]
            except Exception as exc:
                raise RuntimeError(
                    f"Could not load API-Bank level {level} from Hugging Face or "
                    f"the configured cache ({os.environ.get('HF_HUB_CACHE', 'default Hugging Face cache')})."
                ) from exc

    turns: list[APIBankTurn] = []
    for idx, item in enumerate(raw_samples):
        file_name = str(item.get("file", item.get("dialogue_id", f"diag_{idx}"))).replace(".jsonl", "").replace(".json", "")
        t_id = int(item.get("id", item.get("turn_id", idx)))
        unique_id = f"lv{level}_{file_name}_{t_id}"

        exp_out = str(item.get("expected_output", ""))
        parsed_api, parsed_params = parse_api_call(exp_out)

        expected_api = str(item.get("api_name") or parsed_api or "")
        expected_params = dict(item.get("param_dict") or parsed_params or {})

        if item.get("instruction") and item.get("input"):
            prompt = f"{item['instruction'].strip()}\n\n{item['input'].strip()}"
            api_desc = item.get("instruction", "")
            history: list[dict[str, Any]] = []
        else:
            api_desc = str(item.get("api_descriptions", item.get("apis", "")))
            history = list(item.get("history", item.get("dialogue_history", [])))
            prompt = format_api_bank_prompt(api_desc, history)

        turn = APIBankTurn(
            task_id=unique_id,
            level=level,
            dialogue_id=file_name,
            turn_id=t_id,
            api_descriptions=api_desc,
            dialogue_history=history,
            expected_api_name=expected_api,
            expected_param_dict=expected_params,
            prompt=prompt,
        )
        turns.append(turn)

    if task_id is not None:
        turns = [t for t in turns if str(t.task_id) == str(task_id)]
    if start is not None:
        turns = turns[start:]
    if end is not None:
        turns = turns[: end if start is None else end - (start or 0)]
    if limit is not None:
        turns = turns[:limit]

    return turns
