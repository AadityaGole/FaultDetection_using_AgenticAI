"""Programmer agent used for initial code generation and refinement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.common import extract_code_block, load_prompt, normalize_whitespace
from agents.requirement_analyzer import RequirementAnalysis
from dataset.mbpp_loader import MBPPProblem
from llm.client import ChatMessage


@dataclass
class CodeGenerationResult:
    code: str
    raw_response: str
    model: str


class ProgrammerAgent:
    def __init__(self, *, client, model: str) -> None:
        self.client = client
        self.model = model

    def generate(
        self,
        problem: Any,
        analysis: RequirementAnalysis,
        *,
        formal_spec: dict[str, Any] | None = None,
        previous_code: str | None = None,
        feedback: dict[str, Any] | None = None,
    ) -> CodeGenerationResult:
        task_text = getattr(problem, "text", getattr(problem, "prompt", str(problem)))
        entry_point = getattr(problem, "entry_point", None) or "solution"
        prompt = load_prompt("programmer_prompt.txt").format(
            task_text=task_text,
            entry_point=entry_point,
            analysis_summary=analysis.summary,
            formal_spec=formal_spec or {},
            previous_code=previous_code or "",
            feedback=feedback or {},
        )

        response = self.client.chat(
            messages=[
                ChatMessage(role="system", content="You are a software programmer."),
                ChatMessage(role="user", content=prompt),
            ],
            model=self.model,
            temperature=0.2,
            max_tokens=4096,
        )
        return CodeGenerationResult(code=normalize_whitespace(extract_code_block(response)), raw_response=response, model=self.model)
