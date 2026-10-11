"""Artifact management for per-task and per-iteration outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ArtifactPaths:
    task_root: Path
    iteration_dir: Path
    formal_spec_dir: Path
    unit_tests_dir: Path
    property_tests_dir: Path
    final_dir: Path


class ArtifactManager:
    def __init__(self, root: Path, dataset_name: str = "mbpp") -> None:
        self.root = root / dataset_name
        self.root.mkdir(parents=True, exist_ok=True)

    def task_dir(self, task_id: int | str) -> Path:
        path = self.root / str(task_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def iteration_paths(self, task_id: int | str, iteration: int) -> ArtifactPaths:
        task_root = self.task_dir(task_id)
        iteration_dir = task_root / f"iteration_{iteration}"
        formal_spec_dir = iteration_dir / "formal_specification"
        unit_tests_dir = iteration_dir / "unit_tests"
        property_tests_dir = iteration_dir / "property_tests"
        final_dir = task_root / "final"
        for path in [iteration_dir, formal_spec_dir, unit_tests_dir, property_tests_dir, final_dir]:
            path.mkdir(parents=True, exist_ok=True)
        return ArtifactPaths(
            task_root=task_root,
            iteration_dir=iteration_dir,
            formal_spec_dir=formal_spec_dir,
            unit_tests_dir=unit_tests_dir,
            property_tests_dir=property_tests_dir,
            final_dir=final_dir,
        )

    @staticmethod
    def write_text(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def write_json(path: Path, payload: Mapping[str, Any] | list[Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
