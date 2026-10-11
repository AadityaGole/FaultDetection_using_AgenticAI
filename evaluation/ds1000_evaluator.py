"""DS-1000 evaluation harness using official execution context."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dataset.ds1000_loader import DS1000Problem


@dataclass(frozen=True)
class DS1000EvaluationResult:
    passed: bool
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool = False


def adapt_ds1000_code(problem: DS1000Problem, code: str) -> str:
    """If candidate code wraps logic in a function, invoke it and assign to the target variable."""
    import re
    m_prompt = re.findall(r"(\w+)\s*=\s*\.\.\.\s*#\s*put solution in this variable", problem.prompt)
    m_test = re.findall(r"test_env\[['\"](\w+)['\"]\]", problem.code_context)
    target_var = m_prompt[0] if m_prompt else (m_test[0] if m_test else "result")

    m_func = re.search(r"def\s+(\w+)\s*\((.*?)\):", code)
    if m_func and not re.search(rf"\b{target_var}\s*=", code):
        fname = m_func.group(1)
        params = m_func.group(2)
        wrapper = (
            f"\nif '{fname}' in locals():\n"
            f"    try:\n"
            f"        {target_var} = {fname}({params})\n"
            f"    except Exception:\n"
            f"        try:\n"
            f"            {target_var} = {fname}()\n"
            f"        except Exception:\n"
            f"            pass\n"
        )
        return code + "\n" + wrapper
    return code


def evaluate_ds1000(
    problem: DS1000Problem,
    candidate_code: str,
    timeout_seconds: int = 30,
) -> DS1000EvaluationResult:
    """Evaluate candidate solution using the problem's code_context."""
    # Strip any enclosing markdown code blocks if present
    code = candidate_code.strip()
    if code.startswith("```python"):
        code = code[len("```python"):]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()

    code = adapt_ds1000_code(problem, code)

    # Build program following official DS-1000 harness
    program = (
        problem.code_context
        + "\n\n# DS-1000 Candidate Execution\ncode = "
        + repr(code)
        + "\ntry:\n    test_execution(code)\nexcept Exception as _e:\n    raise _e\n"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "ds1000_candidate.py"
        path.write_text(program, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return DS1000EvaluationResult(
                passed=completed.returncode == 0,
                stdout=completed.stdout,
                stderr=completed.stderr,
                returncode=completed.returncode,
            )
        except subprocess.TimeoutExpired as exc:
            return DS1000EvaluationResult(
                passed=False,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "Execution timed out",
                returncode=None,
                timed_out=True,
            )
        except Exception as exc:
            return DS1000EvaluationResult(
                passed=False,
                stdout="",
                stderr=repr(exc),
                returncode=1,
            )
