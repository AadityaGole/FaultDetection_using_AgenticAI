"""Adapter that exposes the formal specification pipeline as a reusable component."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import AppConfig
from dataset.mbpp_loader import MBPPProblem
from formal_spec.pipeline import FormalSpecResult, generate_formal_spec


@dataclass
class FormalSpecAdapterResult:
    problem: Any
    result: FormalSpecResult

    @property
    def formal_spec(self) -> dict[str, Any]:
        return self.result.final_spec

    @property
    def validation_status(self) -> str:
        return self.result.artifacts.validation_status


class FormalSpecAdapter:
    def __init__(self, *, client, config: AppConfig) -> None:
        self.client = client
        self.config = config

    def generate(self, problem: Any, *, model: str) -> FormalSpecAdapterResult:
        result = generate_formal_spec(problem, client=self.client, model=model, config=self.config)
        return FormalSpecAdapterResult(problem=problem, result=result)

