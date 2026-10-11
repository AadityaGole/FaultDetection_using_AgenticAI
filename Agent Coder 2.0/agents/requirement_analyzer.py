"""Requirement analysis stage used before code generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.common import load_prompt
from dataset.mbpp_loader import MBPPProblem
from llm.client import ChatMessage


@dataclass
class RequirementAnalysis:
    summary: str
    constraints: list[str]
    inputs: list[str]
    outputs: list[str]
    edge_cases: list[str]
    raw_response: str | None = None


class RequirementAnalyzer:
    def __init__(self, *, client, model: str) -> None:
        self.client = client
        self.model = model

    def analyze(self, problem: Any, formal_spec: dict[str, Any] | None = None) -> RequirementAnalysis:
        task_text = getattr(problem, "text", getattr(problem, "prompt", str(problem)))
        entry_point = getattr(problem, "entry_point", None) or "solution"
        prompt = load_prompt("requirement_analysis.txt").format(
            task_text=task_text,
            entry_point=entry_point,
            formal_spec=formal_spec or {},
        )
        response = self.client.chat(
            messages=[
                ChatMessage(role="system", content="You are a requirements analyst for programming tasks."),
                ChatMessage(role="user", content=prompt),
            ],
            model=self.model,
            temperature=0.2,
            max_tokens=2048,
        )
        # Lightweight fallback parsing: keep the response as an interpretable summary.
        return RequirementAnalysis(
            summary=response.strip() or task_text,
            constraints=[task_text],
            inputs=[entry_point or "inputs described in the task"],
            outputs=["output described in the task"],
            edge_cases=["empty inputs", "boundary values", "singleton inputs"],
            raw_response=response,
        )

