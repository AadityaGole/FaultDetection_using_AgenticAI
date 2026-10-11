"""BigCodeBench execution-based evaluator."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from dataset.bigcodebench_loader import BigCodeBenchProblem


def parse_unittest_output(stderr: str) -> tuple[int, int]:
    """Parse unittest output to extract total tests and passed count.
    
    Parses output like:
    - "Ran 10 tests in 5.345s\\n\\nOK" -> (10, 10)
    - "Ran 10 tests in 4.629s\\n\\nFAILED (errors=8)" -> (10, 2)
    - "Ran 10 tests\\n\\nFAILED (failures=3, errors=2)" -> (10, 5)
    
    Returns (total_tests, passed_tests)
    """
    matches = list(re.finditer(r'Ran (\d+) test', stderr))
    if not matches:
        return 0, 0
    total_tests = int(matches[-1].group(1))

    # Parse FAILED line: "FAILED (errors=E, failures=F, ...)"
    failed_match = re.search(r'FAILED \((.*?)\)', stderr)
    if failed_match:
        failed_str = failed_match.group(1)
        errors = 0
        failures = 0
        unexpected_successes = 0

        errors_match = re.search(r'errors=(\d+)', failed_str)
        if errors_match:
            errors = int(errors_match.group(1))

        failures_match = re.search(r'failures=(\d+)', failed_str)
        if failures_match:
            failures = int(failures_match.group(1))

        unexp_match = re.search(r'unexpected successes=(\d+)', failed_str)
        if unexp_match:
            unexpected_successes = int(unexp_match.group(1))

        passed = total_tests - errors - failures - unexpected_successes
        return total_tests, max(0, passed)

    if re.search(r'(?:^|\n)FAILED\b', stderr):
        return total_tests, 0

    if '\nOK' in stderr or re.search(r'(?:^|\n)OK(?:\s*\(.*?\))?\s*$', stderr.strip()):
        return total_tests, total_tests

    return total_tests, 0


@dataclass(frozen=True)
class BigCodeBenchEvaluationResult:
    passed: bool
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool = False
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0


def build_bigcodebench_eval_code(problem: BigCodeBenchProblem, candidate_code: str) -> str:
    test_code = problem.test.strip()
    parts = [
        "import unittest",
        candidate_code.strip(),
        test_code,
        "\nif __name__ == '__main__':\n    unittest.main()\n",
    ]
    return "\n\n".join(part for part in parts if part)


def evaluate_bigcodebench(
    problem: BigCodeBenchProblem,
    candidate_code: str,
    timeout_seconds: int = 30,
) -> BigCodeBenchEvaluationResult:
    code = build_bigcodebench_eval_code(problem, candidate_code)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "bigcodebench_candidate.py"
        path.write_text(code, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            total, passed = parse_unittest_output(completed.stderr)
            return BigCodeBenchEvaluationResult(
                passed=completed.returncode == 0,
                stdout=completed.stdout,
                stderr=completed.stderr,
                returncode=completed.returncode,
                total_tests=total,
                passed_tests=passed,
                failed_tests=max(0, total - passed),
            )
        except subprocess.TimeoutExpired as exc:
            # Ensure stdout/stderr are strings (handle both str and bytes)
            stdout_str = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout.decode("utf-8", errors="replace") if exc.stdout else "")
            stderr_str = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else "Execution timed out")
            total, passed = parse_unittest_output(stderr_str)
            return BigCodeBenchEvaluationResult(
                passed=False,
                stdout=stdout_str,
                stderr=stderr_str or "Execution timed out",
                returncode=None,
                timed_out=True,
                total_tests=total,
                passed_tests=passed,
                failed_tests=max(0, total - passed),
            )
