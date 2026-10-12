"""Test execution for unit tests and property-based tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Sequence

from dataset.mbpp_loader import MBPPProblem
from evaluation.bigcodebench_evaluator import parse_unittest_output


@dataclass
class ExecutionSection:
    passed: int = 0
    failed: int = 0
    failures: list[dict[str, Any]] | None = None
    stdout: str = ""
    stderr: str = ""


@dataclass
class ExecutionReport:
    unit_tests: ExecutionSection
    property_tests: ExecutionSection
    runtime_errors: list[str]
    timeouts: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_tests": asdict(self.unit_tests),
            "property_tests": asdict(self.property_tests),
            "runtime_errors": self.runtime_errors,
            "timeouts": self.timeouts,
        }


class BenchmarkExecutor:
    def __init__(self, *, timeout_seconds: int) -> None:
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _compile_bundle(code: str, label: str) -> tuple[bool, str | None]:
        try:
            compile(code, f"<{label}>", "exec")
            return True, None
        except SyntaxError as exc:
            return False, f"{label} SyntaxError: {exc.msg} (line {exc.lineno}, column {exc.offset})"
        except Exception as exc:  # pragma: no cover - defensive
            return False, f"{label} compile error: {type(exc).__name__}: {exc}"

    def _run(
        self,
        code: str,
        entry_point: str | None = None,
        implementation: str = "",
        python_paths: Sequence[Path] = (),
    ) -> tuple[int | None, str, str, bool]:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_bundle.py"
            path.write_text(code, encoding="utf-8")
            if entry_point and implementation:
                try:
                    (Path(tmpdir) / f"{entry_point}.py").write_text(implementation, encoding="utf-8")
                except Exception:
                    pass
            env = os.environ.copy()
            if python_paths:
                existing_pythonpath = env.get("PYTHONPATH", "")
                paths = [str(path.resolve()) for path in python_paths]
                if existing_pythonpath:
                    paths.append(existing_pythonpath)
                env["PYTHONPATH"] = os.pathsep.join(paths)
            try:
                completed = subprocess.run(
                    [sys.executable, str(path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                    cwd=tmpdir,
                    env=env,
                )
                return completed.returncode, completed.stdout, completed.stderr, False
            except subprocess.TimeoutExpired as exc:
                return None, exc.stdout or "", exc.stderr or "Timed out", True

    def _execute_suite(
        self,
        *,
        label: str,
        implementation: str,
        tests: str,
        auto_caller: str,
        entry_point: str | None,
        python_paths: Sequence[Path],
    ) -> tuple[ExecutionSection, str | None, bool]:
        if not tests.strip():
            if label == "property_tests":
                return ExecutionSection(), None, False
            message = f"{label} source is empty; no tests were executed."
            return (
                ExecutionSection(
                    failed=1,
                    failures=[{"stderr": message, "stdout": ""}],
                    stderr=message,
                ),
                message,
                False,
            )

        bundle = implementation + "\n\n" + tests + auto_caller
        compiled, compile_error = self._compile_bundle(bundle, label)
        if not compiled:
            error = compile_error or f"{label} bundle failed to compile."
            return (
                ExecutionSection(
                    failed=1,
                    failures=[{"stderr": error, "stdout": ""}],
                    stderr=error,
                ),
                error,
                False,
            )

        return_code, stdout, stderr, timed_out = self._run(
            bundle,
            entry_point=entry_point,
            implementation=implementation,
            python_paths=python_paths,
        )
        total, passed = parse_unittest_output(stderr)
        if total > 0:
            failed = total - passed
        else:
            passed = 1 if return_code == 0 else 0
            failed = 0 if return_code == 0 else 1
        failures = (
            []
            if failed == 0
            else [{"stderr": stderr or f"{label} process exited with code {return_code}.", "stdout": stdout}]
        )
        runtime_error = (
            stderr or f"{label} process exited with code {return_code}."
            if return_code not in (0, None)
            else None
        )
        section = ExecutionSection(
            passed=passed,
            failed=failed,
            failures=failures,
            stdout=stdout,
            stderr=stderr,
        )
        return section, runtime_error, timed_out

    def execute(
        self,
        *,
        implementation: str,
        unit_tests: str,
        property_tests: str | None,
        entry_point: str | None = None,
        python_paths: Sequence[Path] = (),
    ) -> ExecutionReport:
        auto_caller = """

if __name__ == '__main__':
    import unittest, sys
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for _k, _v in list(globals().items()):
        if isinstance(_v, type) and issubclass(_v, unittest.TestCase) and _v is not unittest.TestCase:
            suite.addTests(loader.loadTestsFromTestCase(_v))
        elif _k.startswith('test_') and callable(_v):
            suite.addTest(unittest.FunctionTestCase(_v))
    if suite.countTestCases() > 0:
        runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=1)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
"""
        unit_section, unit_error, unit_timeout = self._execute_suite(
            label="unit_tests",
            implementation=implementation,
            tests=unit_tests,
            auto_caller=auto_caller,
            entry_point=entry_point,
            python_paths=python_paths,
        )
        property_section, property_error, property_timeout = self._execute_suite(
            label="property_tests",
            implementation=implementation,
            tests=property_tests or "",
            auto_caller=auto_caller,
            entry_point=entry_point,
            python_paths=python_paths,
        )
        runtime_errors = [error for error in (unit_error, property_error) if error]
        timeouts = [
            label
            for label, did_timeout in (
                ("unit_tests", unit_timeout),
                ("property_tests", property_timeout),
            )
            if did_timeout
        ]
        return ExecutionReport(
            unit_tests=unit_section,
            property_tests=property_section,
            runtime_errors=runtime_errors,
            timeouts=timeouts,
        )
