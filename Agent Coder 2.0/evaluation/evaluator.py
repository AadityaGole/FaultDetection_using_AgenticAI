"""MBPP evaluation utilities that keep reference tests isolated from generation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from dataset.mbpp_loader import MBPPProblem


@dataclass(frozen=True)
class EvaluationResult:
    passed: bool
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool = False
    test_name: str | None = None


def _run_python(code: str, timeout_seconds: int) -> EvaluationResult:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "candidate.py"
        path.write_text(code, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return EvaluationResult(
                passed=completed.returncode == 0,
                stdout=completed.stdout,
                stderr=completed.stderr,
                returncode=completed.returncode,
            )
        except subprocess.TimeoutExpired as exc:
            return EvaluationResult(
                passed=False,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "Timed out",
                returncode=None,
                timed_out=True,
            )


def build_mbpp_eval_code(problem: MBPPProblem, candidate_code: str, use_challenge_tests: bool = True) -> str:
    tests = problem.challenge_test_list if use_challenge_tests and problem.challenge_test_list else problem.test_list or []
    setup = problem.test_setup_code or ""
    parts = [setup, candidate_code, "\n".join(tests)]
    return "\n\n".join(part for part in parts if part)


def evaluate_mbpp(problem: MBPPProblem, candidate_code: str, timeout_seconds: int = 10) -> EvaluationResult:
    code = build_mbpp_eval_code(problem, candidate_code)
    return _run_python(code, timeout_seconds=timeout_seconds)
