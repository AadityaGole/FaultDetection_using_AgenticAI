"""API-Bank generation, direct evaluation, and extended AgentCoder test stages."""

from __future__ import annotations

import ast
import json
import re
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents.api_bank_call_agent import APIBankCallAgent
from agents.property_test_agent import PropertyTestAgent
from agents.requirement_analyzer import RequirementAnalyzer
from agents.test_executor import BenchmarkExecutor
from agents.unit_test_agent import UnitTestAgent
from config import AppConfig
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank
from formal_spec.adapter import FormalSpecAdapter

PIPELINE_VERSION = 6

class RequestPacer:
    """Enforce a shared minimum interval between all outbound model requests."""

    def __init__(self, requests_per_minute: float) -> None:
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be greater than zero")
        self._interval = 60.0 / requests_per_minute
        self._next_request = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            scheduled = max(now, self._next_request)
            self._next_request = scheduled + self._interval
        delay = scheduled - now
        if delay > 0:
            time.sleep(delay)

class RateLimitedLLMClient:
    """Route every agent request and retry through the shared run-level pacer."""

    def __init__(self, client: Any, pacer: RequestPacer) -> None:
        self._client = client
        self._pacer = pacer

    def chat(self, **kwargs: Any) -> str:
        kwargs["request_hook"] = self._pacer.wait
        return self._client.chat(**kwargs)

@dataclass(frozen=True)
class APIBankTestProblem:
    task_id: str
    entry_point: str
    text: str

def _strip_api_bank_evaluator_imports(source: str) -> str:
    try:
        module = ast.parse(source)
    except SyntaxError:
        return source

    evaluator_modules = {
        "evaluate.api_bank_evaluator",
        "evaluation.api_bank_evaluator",
    }
    lines = source.splitlines(keepends=True)
    import_ranges = [
        (node.lineno - 1, node.end_lineno)
        for node in ast.walk(module)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module in evaluator_modules
        )
        or (
            isinstance(node, ast.Import)
            and any(alias.name in evaluator_modules for alias in node.names)
        )
    ]
    for start, end in sorted(set(import_ranges), reverse=True):
        del lines[start:end]
    return "".join(lines)

def _has_unit_evaluator_assertions(source: str) -> bool:
    try:
        module = ast.parse(source)
    except SyntaxError:
        return False
    for test in module.body:
        if not isinstance(test, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not test.name.startswith("test_"):
            continue
        candidate_bound = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "evaluate_api_call"
            and not node.args
            and not node.keywords
            for node in ast.walk(test)
        )
        candidate_pass_asserted = any(
            isinstance(node, ast.Assert)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Attribute)
            and node.test.left.attr == "passed"
            and any(
                isinstance(comparator, ast.Constant) and comparator.value is True
                for comparator in node.test.comparators
            )
            for node in ast.walk(test)
        )
        if candidate_bound and candidate_pass_asserted:
            return True
    return False

def _has_property_evaluator_assertions(source: str) -> bool:
    try:
        module = ast.parse(source)
    except SyntaxError:
        return False
    for test in module.body:
        if not isinstance(test, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not test.name.startswith("test_"):
            continue
        has_hypothesis_decorator = any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "given"
            for decorator in test.decorator_list
        )
        if not has_hypothesis_decorator:
            continue
        calls_evaluator = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "evaluate_api_call"
            for node in ast.walk(test)
        )
        asserts_evaluator_result = any(
            isinstance(node, ast.Assert)
            and any(
                isinstance(child, ast.Attribute)
                and child.attr in {"passed", "api_match", "params_match", "parsed_api_name"}
                for child in ast.walk(node.test)
            )
            for node in ast.walk(test)
        )
        if calls_evaluator and asserts_evaluator_result:
            return True
    return False

def _unit_tests_passed(source: str, section: Any) -> bool:
    try:
        module = ast.parse(source)
    except SyntaxError:
        return False
    has_test = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in module.body
    )
    return (
        has_test
        and _has_unit_evaluator_assertions(source)
        and section.passed > 0
        and section.failed == 0
    )

def _property_tests_passed(source: str, section: Any) -> bool:
    return (
        _has_property_evaluator_assertions(source)
        and section.passed > 0
        and section.failed == 0
    )

def _make_test_problem(problem: APIBankTurn) -> APIBankTestProblem:
    return APIBankTestProblem(
        task_id=str(problem.task_id),
        entry_point="evaluate_api_call",
        text=(
            f"API-Bank task and dialogue:\n{problem.prompt}\n\n"
            "The candidate is an API-call string. The provided implementation defines "
            "evaluate_api_call(candidate=None), which invokes the repository's canonical "
            "evaluation.api_bank_evaluator.evaluate_api_bank against this exact dataset turn. "
            "Its result exposes passed, parsed_api_name, parsed_params, api_match, and "
            "params_match as object attributes (for example, result.passed), not dictionary "
            "keys. Do not call .get() or subscript this result. API-Bank correctness requires "
            "a parseable call, the exact expected "
            "API name (case-insensitive), the exact expected parameter map after string "
            "normalization, and successful mock-schema execution. Unit tests must include a "
            "correctness gate that calls evaluate_api_call() with no candidate override and "
            "asserts result.passed is exactly True. The property-test agent must use the "
            "formal specification below to derive Hypothesis properties of the canonical "
            "evaluator. Do not invent API side effects or substitute another evaluator."
        ),
    )

def _build_test_harness(problem: APIBankTurn, generated_api_call: str) -> str:
    turn_json = json.dumps(problem.evaluation_view(), ensure_ascii=False)
    return (
        "import json\n"
        "from dataset.api_bank_loader import APIBankTurn\n"
        "from evaluation.api_bank_evaluator import evaluate_api_bank\n\n"
        f"_api_bank_turn = APIBankTurn(**json.loads({turn_json!r}))\n"
        f"_generated_api_call = {generated_api_call!r}\n\n"
        "def api_call():\n"
        "    return _generated_api_call\n\n"
        "def evaluate_api_call(candidate=None):\n"
        "    output = api_call() if candidate is None else candidate\n"
        "    return evaluate_api_bank(_api_bank_turn, output)\n"
    )

def _run_task(
    problem: APIBankTurn,
    client: Any,
    model: str,
    pacer: RequestPacer,
    config: AppConfig,
    cached_call: str | None = None,
) -> dict[str, Any]:
    limited_client = RateLimitedLLMClient(client, pacer)
    call_source = "reused" if cached_call is not None else "generated"
    stage_errors: dict[str, str] = {}
    agent_outputs: dict[str, Any] = {}
    generated_api_call = ""

    test_problem = _make_test_problem(problem)
    try:
        requirements = RequirementAnalyzer(
            client=limited_client,
            model=config.resolve_model("code_generation"),
        ).analyze(test_problem)
        if not requirements.summary.strip():
            raise ValueError("Requirement analysis returned an empty summary.")
        agent_outputs["requirement_analysis"] = {
            "summary": requirements.summary,
            "raw_response": requirements.raw_response,
            "model": config.resolve_model("code_generation"),
        }
    except Exception as exc:
        requirements = None
        stage_errors["requirement_analysis"] = f"{type(exc).__name__}: {exc}"

    try:
        if cached_call is None:
            if requirements is None:
                raise RuntimeError("API-call generation blocked because requirement analysis failed.")
            call_result = APIBankCallAgent(
                client=limited_client,
                model=model,
            ).generate(problem, requirements)
            generated_api_call = call_result.raw_response
            agent_outputs["api_call_generation"] = {
                "raw_response": call_result.raw_response,
                "model": call_result.model,
            }
        else:
            generated_api_call = cached_call
            agent_outputs["api_call_generation"] = {
                "raw_response": cached_call,
                "model": None,
                "reused": True,
            }
    except Exception as exc:
        stage_errors["api_call_generation"] = f"{type(exc).__name__}: {exc}"

    generated_api_call = generated_api_call.strip()
    empty_response = not generated_api_call
    evaluation = evaluate_api_bank(problem, generated_api_call)

    formal_spec: dict[str, Any] = {}
    formal_spec_status = "failed"
    try:
        formal_spec_result = FormalSpecAdapter(
            client=limited_client,
            config=config,
        ).generate(test_problem, model=config.resolve_model("formal_spec"))
        formal_spec = formal_spec_result.formal_spec
        formal_spec_status = formal_spec_result.validation_status
        agent_outputs["formal_specification"] = {
            "validation_status": formal_spec_status,
            "validation_errors": formal_spec_result.result.artifacts.validation_errors,
            "refinement_attempts": formal_spec_result.result.artifacts.refinement_attempts,
            "raw_responses": formal_spec_result.result.raw_responses,
            "model": config.resolve_model("formal_spec"),
        }
    except Exception as exc:
        stage_errors["formal_specification"] = f"{type(exc).__name__}: {exc}"

    implementation = _build_test_harness(problem, generated_api_call)

    unit_tests = ""
    property_tests = ""
    test_results: dict[str, Any] = {
        "report": {},
        "unit_tests_passed": False,
        "property_tests_passed": False,
        "test_validation_errors": [],
    }
    try:
        unit_result = UnitTestAgent(
            client=limited_client,
            model=config.resolve_model("unit_test"),
        ).generate(
            test_problem,
            implementation_code=implementation,
            requirements_summary=(
                requirements.summary if requirements is not None else ""
            ),
            formal_spec=formal_spec,
        )
        unit_tests = _strip_api_bank_evaluator_imports(unit_result.code)
        agent_outputs["unit_test_generation"] = {
            "raw_response": unit_result.raw_response,
            "model": unit_result.model,
        }
    except Exception as exc:
        stage_errors["unit_test_generation"] = f"{type(exc).__name__}: {exc}"

    try:
        property_result = PropertyTestAgent(
            client=limited_client,
            model=config.resolve_model("property_test"),
        ).generate(test_problem, formal_spec)
        property_tests = _strip_api_bank_evaluator_imports(property_result.code)
        agent_outputs["property_test_generation"] = {
            "raw_response": property_result.raw_response,
            "model": property_result.model,
            "formal_spec_validation_status": formal_spec_status,
        }
    except Exception as exc:
        stage_errors["property_test_generation"] = f"{type(exc).__name__}: {exc}"

    try:
        report = BenchmarkExecutor(
            timeout_seconds=config.test_timeout_seconds
        ).execute(
            implementation=implementation,
            unit_tests=unit_tests,
            property_tests=property_tests,
            entry_point=test_problem.entry_point,
            python_paths=(Path(__file__).resolve().parent,),
        )
        report_data = report.to_dict()
        unit_tests_passed = (
            _unit_tests_passed(unit_tests, report.unit_tests)
            and formal_spec_status in {"validated", "validated_after_repair"}
        )
        property_tests_passed = (
            _property_tests_passed(property_tests, report.property_tests)
            and formal_spec_status in {"validated", "validated_after_repair"}
        )
        unit_contract_valid = _has_unit_evaluator_assertions(unit_tests)
        property_contract_valid = _has_property_evaluator_assertions(property_tests)
        test_validation_errors: list[str] = []
        if not unit_contract_valid:
            test_validation_errors.append(
                "Unit tests must assert that evaluate_api_call() passes for the candidate."
            )
        if not property_contract_valid:
            test_validation_errors.append(
                "Property tests must use Hypothesis and assert evaluator-result properties "
                "grounded in the formal specification."
            )
        test_results = {
            "report": report_data,
            "unit_tests_passed": unit_tests_passed and unit_contract_valid,
            "property_tests_passed": property_tests_passed and property_contract_valid,
            "test_validation_errors": test_validation_errors,
            "formal_spec_passed": formal_spec_status
            in {"validated", "validated_after_repair"},
        }
    except Exception as exc:
        stage_errors["test_execution"] = f"{type(exc).__name__}: {exc}"
        test_results["test_validation_errors"].append(stage_errors["test_execution"])

    api_call_status = (
        "empty_response"
        if empty_response and isinstance(
            stage_errors.get("api_call_generation", ""), str
        ) and "LLMEmptyResponseError" in stage_errors.get("api_call_generation", "")
        else "request_failed"
        if empty_response and "api_call_generation" in stage_errors
        else "empty_response"
        if empty_response
        else "valid"
        if evaluation.passed
        else "invalid"
    )
    request_status = (
        "failed"
        if empty_response and "api_call_generation" in stage_errors
        else "reused"
        if call_source == "reused"
        else "success"
    )
    formal_spec_passed = formal_spec_status in {"validated", "validated_after_repair"}
    unit_passed = test_results["unit_tests_passed"]
    property_passed = test_results["property_tests_passed"]
    requirements_passed = requirements is not None
    passed = (
        evaluation.passed
        and requirements_passed
        and formal_spec_passed
        and unit_passed
        and property_passed
    )
    error = evaluation.error
    if stage_errors:
        error = "; ".join(
            f"{stage}: {message}" for stage, message in stage_errors.items()
        )
    if error is None and not unit_passed:
        error = "Generated unit tests failed validation or execution"
    if error is None and not property_passed:
        error = "Generated property tests failed validation or execution"
    if error is None and not formal_spec_passed:
        error = f"Formal specification validation failed: {formal_spec_status}"
    return {
        "pipeline_version": PIPELINE_VERSION,
        "task_id": problem.task_id,
        "pipeline_status": "incomplete" if stage_errors else "completed",
        "api_call_source": call_source,
        "api_call_status": api_call_status,
        "request_status": request_status,
        "failure_stage": next(iter(stage_errors), None),
        "generated_api_call": generated_api_call,
        "generated_code": implementation,
        "formal_spec": formal_spec,
        "unit_tests": unit_tests,
        "property_tests": property_tests,
        "test_execution_report": test_results["report"],
        "agent_outputs": agent_outputs,
        "stage_errors": stage_errors,
        "evaluation": {
            "passed": passed,
            "parsed_api_name": evaluation.parsed_api_name,
            "parsed_params": evaluation.parsed_params,
            "api_match": evaluation.api_match,
            "params_match": evaluation.params_match,
            "requirements_analysis_passed": requirements_passed,
            "formal_spec_passed": formal_spec_passed,
            "unit_tests_passed": unit_passed,
            "property_tests_passed": property_passed,
            "test_validation_errors": test_results["test_validation_errors"],
            "error": error,
        },
    }

def run_api_bank_direct(
    problems: list[APIBankTurn],
    *,
    client: Any,
    model: str,
    output_root: Path,
    config: AppConfig,
    workers: int = 3,
    requests_per_minute: float = 5,
    resume: bool = False,
    reuse_generated_dir: Path | None = None,
) -> dict[str, Any]:
    if workers < 1:
        raise ValueError("workers must be at least 1")
    if requests_per_minute <= 0:
        raise ValueError("requests_per_minute must be greater than zero")
    if not problems:
        return {"total": 0, "passed": 0, "results": []}

    summary_path = output_root / "run_summary.json"
    temporary_path = summary_path.with_suffix(".json.tmp")
    existing_results: list[dict[str, Any]] = []
    if summary_path.exists():
        if not resume:
            raise FileExistsError(
                f"{summary_path} already exists; choose a fresh output directory or pass --resume."
            )
        existing_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        existing_results = existing_summary.get("results", [])
        if temporary_path.exists():
            try:
                temporary_summary = json.loads(temporary_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                print(
                    f"Ignoring invalid interrupted checkpoint {temporary_path}: {exc}",
                    flush=True,
                )
            else:
                saved_count = len(existing_results)
                temporary_results = temporary_summary.get("results", [])
                if len(temporary_results) > saved_count:
                    existing_results = temporary_results
                    print(
                        f"Recovering {len(existing_results)} saved task results "
                        f"from interrupted checkpoint {temporary_path}.",
                        flush=True,
                    )

    reusable_results: list[dict[str, Any]] = []
    if reuse_generated_dir is not None:
        reuse_path = reuse_generated_dir / f"api_bank_level_{problems[0].level}" / "run_summary.json"
        if not reuse_path.is_file():
            raise FileNotFoundError(f"Saved API-Bank responses not found: {reuse_path}")
        reusable_summary = json.loads(reuse_path.read_text(encoding="utf-8"))
        reusable_results = reusable_summary.get("results", [])

    problem_by_id = {str(problem.task_id): problem for problem in problems}
    reusable_by_id = {
        str(result.get("task_id")): result
        for result in reusable_results
        if result.get("request_status") == "success" and result.get("generated_api_call")
    }
    completed_results = {
        str(result.get("task_id")): result
        for result in existing_results
        if str(result.get("task_id")) in problem_by_id
        and result.get("pipeline_version") == PIPELINE_VERSION
        and result.get("pipeline_status") == "completed"
    }
    pending = [
        problem
        for problem in problems
        if str(problem.task_id) not in completed_results
    ]
    pacer = RequestPacer(requests_per_minute)
    output_root.mkdir(parents=True, exist_ok=True)

    def save_summary() -> dict[str, Any]:
        ordered = [
            completed_results[str(problem.task_id)]
            for problem in problems
            if str(problem.task_id) in completed_results
        ]
        passed = sum(bool(result.get("evaluation", {}).get("passed")) for result in ordered)
        summary = {
            "pipeline_version": PIPELINE_VERSION,
            "dataset": "api_bank",
            "mode": "agentic_api_bank",
            "workers": workers,
            "requests_per_minute": requests_per_minute,
            "total": len(ordered),
            "expected_total": len(problems),
            "passed": passed,
            "accuracy": f"{(passed / len(ordered) * 100.0) if ordered else 0.0:.2f}%",
            "successful_requests": sum(
                result.get("request_status") == "success" for result in ordered
            ),
            "failed_requests": sum(
                result.get("request_status") == "failed" for result in ordered
            ),
            "reused_calls": sum(
                result.get("request_status") == "reused" for result in ordered
            ),
            "invalid_api_calls": sum(
                result.get("api_call_status") == "invalid" for result in ordered
            ),
            "empty_api_responses": sum(
                result.get("api_call_status") == "empty_response" for result in ordered
            ),
            "generation_request_failures": sum(
                result.get("api_call_status") == "request_failed" for result in ordered
            ),
            "worker_failures": sum(
                result.get("failure_stage") == "worker_execution" for result in ordered
            ),
            "incomplete_tasks": sum(
                result.get("pipeline_status") != "completed" for result in ordered
            ),
            "requirement_analysis_failures": sum(
                not result.get("evaluation", {}).get(
                    "requirements_analysis_passed", False
                )
                for result in ordered
            ),
            "formal_spec_failures": sum(
                not result.get("evaluation", {}).get("formal_spec_passed", False)
                for result in ordered
            ),
            "unit_test_generation_failures": sum(
                "unit_test_generation" in result.get("stage_errors", {})
                for result in ordered
            ),
            "property_test_generation_failures": sum(
                "property_test_generation" in result.get("stage_errors", {})
                for result in ordered
            ),
            "unit_test_failures": sum(
                not result.get("evaluation", {}).get("unit_tests_passed", False)
                for result in ordered
            ),
            "property_test_failures": sum(
                not result.get("evaluation", {}).get("property_tests_passed", False)
                for result in ordered
            ),
            "results": ordered,
        }
        temporary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        try:
            temporary_path.replace(summary_path)
        except PermissionError as exc:
            print(
                f"WARNING: Could not replace {summary_path}: {exc}. "
                f"The current checkpoint remains at {temporary_path} and will be recovered on resume.",
                flush=True,
            )
        return summary

    if completed_results:
        save_summary()

    reused_calls = sum(str(problem.task_id) in reusable_by_id for problem in pending)
    new_calls = len(pending) - reused_calls
    print(
        f"Starting extended API-Bank run: {len(pending)} tasks pending "
        f"({reused_calls} saved calls reused, {new_calls} new calls); "
        f"{workers} workers; capped at {requests_per_minute:g} requests/minute.",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for problem in pending:
            saved = reusable_by_id.get(str(problem.task_id))
            cached_call = saved.get("generated_api_call") if saved else None
            future = executor.submit(
                _run_task,
                problem,
                client,
                model,
                pacer,
                config,
                cached_call,
            )
            futures[future] = problem

        completed = len(completed_results)
        for future in as_completed(futures):
            problem = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                error_traceback = traceback.format_exc()
                result = {
                    "pipeline_version": PIPELINE_VERSION,
                    "task_id": problem.task_id,
                    "pipeline_status": "failed",
                    "api_call_source": "generated",
                    "api_call_status": "worker_error",
                    "request_status": "unknown",
                    "failure_stage": "worker_execution",
                    "generated_api_call": "",
                    "worker_error": error_traceback,
                    "evaluation": {
                        "passed": False,
                        "parsed_api_name": None,
                        "parsed_params": {},
                        "api_match": False,
                        "params_match": False,
                        "unit_tests_passed": False,
                        "property_tests_passed": False,
                        "error": f"Worker crashed: {type(exc).__name__}: {exc}",
                    },
                }
                print(
                    f"Worker failed for task {problem.task_id}: "
                    f"{type(exc).__name__}: {exc}; "
                    "continuing with remaining tasks.",
                    flush=True,
                )
            completed_results[str(problem.task_id)] = result
            summary = save_summary()
            completed += 1

            task_dir = output_root / str(problem.task_id)
            task_dir.mkdir(parents=True, exist_ok=True)
            if "worker_error" in result:
                (task_dir / "worker_error.txt").write_text(
                    result["worker_error"], encoding="utf-8"
                )
            (task_dir / "generated_api_call.txt").write_text(
                result.get("generated_api_call", ""), encoding="utf-8"
            )
            for key, filename in (
                ("generated_code", "generated_code.py"),
                ("unit_tests", "unit_tests.py"),
                ("property_tests", "property_tests.py"),
            ):
                if key in result:
                    (task_dir / filename).write_text(result[key], encoding="utf-8")
            for key, filename in (
                ("formal_spec", "formal_spec.json"),
                ("test_execution_report", "test_execution_report.json"),
                ("agent_outputs", "agent_outputs.json"),
                ("stage_errors", "stage_errors.json"),
            ):
                if key in result:
                    (task_dir / filename).write_text(
                        json.dumps(result[key], indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )

            evaluation = result.get("evaluation", {})
            print(
                f"[{completed}/{len(problems)}] Task {problem.task_id}: "
                f"{'PASSED' if evaluation.get('passed') else 'FAILED'} | "
                f"CALL={result.get('api_call_status', 'unknown')} "
                f"source={result.get('api_call_source', 'unknown')} "
                f"spec={evaluation.get('formal_spec_passed', False)} "
                f"API={evaluation.get('api_match', False)} "
                f"params={evaluation.get('params_match', False)} "
                f"unit={evaluation.get('unit_tests_passed', False)} "
                f"property={evaluation.get('property_tests_passed', False)} | "
                f"Current: {summary['passed']}/{summary['total']} ({summary['accuracy']}) | "
                f"API requests: {summary['successful_requests']} non-empty, "
                f"{summary['failed_requests']} failed/empty; reused: {summary['reused_calls']} | "
                f"Invalid calls: {summary['invalid_api_calls']}; "
                f"Unit failures: {summary['unit_test_failures']}; "
                f"Property failures: {summary['property_test_failures']}",
                flush=True,
            )

    final_summary = save_summary()
    print(f"Run complete. Summary saved to {summary_path}", flush=True)
    return final_summary
