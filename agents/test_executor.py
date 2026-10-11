"""Test execution for unit tests and property-based tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

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

    def _run(self, code: str, entry_point: str | None = None, implementation: str = "") -> tuple[int | None, str, str, bool]:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_bundle.py"
            path.write_text(code, encoding="utf-8")
            if entry_point and implementation:
                try:
                    (Path(tmpdir) / f"{entry_point}.py").write_text(implementation, encoding="utf-8")
                except Exception:
                    pass
            try:
                completed = subprocess.run(
                    [sys.executable, str(path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                    cwd=tmpdir,
                )
                return completed.returncode, completed.stdout, completed.stderr, False
            except subprocess.TimeoutExpired as exc:
                return None, exc.stdout or "", exc.stderr or "Timed out", True

    def execute(self, *, implementation: str, unit_tests: str, property_tests: str | None, entry_point: str | None = None) -> ExecutionReport:
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

        unit_bundle = implementation + "\n\n" + unit_tests + auto_caller
        prop_bundle = (implementation + "\n\n" + property_tests + auto_caller) if property_tests and property_tests.strip() else ""

        unit_ok, unit_compile_error = self._compile_bundle(unit_bundle, "unit_tests")
        prop_ok, prop_compile_error = (True, None)
        if prop_bundle.strip():
            prop_ok, prop_compile_error = self._compile_bundle(prop_bundle, "property_tests")

        if not unit_ok:
            return ExecutionReport(
                unit_tests=ExecutionSection(
                    passed=0,
                    failed=1,
                    failures=[{"stderr": unit_compile_error or "Unit test bundle failed to compile", "stdout": ""}],
                    stderr=unit_compile_error or "Unit test bundle failed to compile",
                ),
                property_tests=ExecutionSection(
                    passed=0,
                    failed=0 if not prop_bundle.strip() else 1,
                    failures=[] if not prop_bundle.strip() else [{"stderr": "Skipped because unit tests did not compile", "stdout": ""}],
                    stderr="" if not prop_bundle.strip() else "Skipped because unit tests did not compile",
                ),
                runtime_errors=[unit_compile_error] if unit_compile_error else [],
                timeouts=[],
            )

        if prop_bundle.strip() and not prop_ok:
            unit_rc, unit_out, unit_err, unit_timeout = self._run(unit_bundle, entry_point=entry_point, implementation=implementation)
            unit_total, unit_passed = parse_unittest_output(unit_err)
            if unit_total > 0:
                unit_failed = unit_total - unit_passed
                unit_failures = [] if unit_failed == 0 else [{"stderr": unit_err, "stdout": unit_out}]
            else:
                unit_passed = 1 if unit_rc == 0 else 0
                unit_failed = 0 if unit_rc == 0 else 1
                unit_failures = [] if unit_rc == 0 else [{"stderr": unit_err, "stdout": unit_out}]

            return ExecutionReport(
                unit_tests=ExecutionSection(
                    passed=unit_passed,
                    failed=unit_failed,
                    failures=unit_failures,
                    stdout=unit_out,
                    stderr=unit_err,
                ),
                property_tests=ExecutionSection(
                    passed=0,
                    failed=1,
                    failures=[{"stderr": prop_compile_error or "Property test bundle failed to compile", "stdout": ""}],
                    stderr=prop_compile_error or "Property test bundle failed to compile",
                ),
                runtime_errors=[err for err in [unit_err if unit_rc not in (0, None) else None, prop_compile_error] if err],
                timeouts=["unit_tests"] if unit_timeout else [],
            )

        unit_rc, unit_out, unit_err, unit_timeout = self._run(unit_bundle, entry_point=entry_point, implementation=implementation)

        if prop_bundle.strip():
            prop_rc, prop_out, prop_err, prop_timeout = self._run(prop_bundle, entry_point=entry_point, implementation=implementation)
        else:
            prop_rc, prop_out, prop_err, prop_timeout = 0, "", "", False

        unit_total, unit_passed = parse_unittest_output(unit_err)
        if unit_total > 0:
            unit_failed = unit_total - unit_passed
            unit_failures = [] if unit_failed == 0 else [{"stderr": unit_err, "stdout": unit_out}]
        else:
            unit_passed = 1 if unit_rc == 0 else 0
            unit_failed = 0 if unit_rc == 0 else 1
            unit_failures = [] if unit_rc == 0 else [{"stderr": unit_err, "stdout": unit_out}]

        unit_section = ExecutionSection(
            passed=unit_passed,
            failed=unit_failed,
            failures=unit_failures,
            stdout=unit_out,
            stderr=unit_err,
        )

        if prop_bundle.strip() == "":
            property_section = ExecutionSection(
                passed=0,
                failed=0,
                failures=[],
                stdout="",
                stderr="",
            )
        else:
            prop_total, prop_passed = parse_unittest_output(prop_err)
            if prop_total > 0:
                prop_failed = prop_total - prop_passed
                prop_failures = [] if prop_failed == 0 else [{"stderr": prop_err, "stdout": prop_out}]
            else:
                prop_passed = 1 if prop_rc == 0 else 0
                prop_failed = 0 if prop_rc == 0 else 1
                prop_failures = [] if prop_rc == 0 else [{"stderr": prop_err, "stdout": prop_out}]

            property_section = ExecutionSection(
                passed=prop_passed,
                failed=prop_failed,
                failures=prop_failures,
                stdout=prop_out,
                stderr=prop_err,
            )

        runtime_errors: list[str] = []
        timeouts: list[str] = []
        if unit_err and unit_rc not in (0, None):
            runtime_errors.append(unit_err)
        if prop_err and prop_rc not in (0, None):
            runtime_errors.append(prop_err)
        if unit_timeout:
            timeouts.append("unit_tests")
        if prop_timeout:
            timeouts.append("property_tests")

        return ExecutionReport(
            unit_tests=unit_section,
            property_tests=property_section,
            runtime_errors=runtime_errors,
            timeouts=timeouts,
        )
