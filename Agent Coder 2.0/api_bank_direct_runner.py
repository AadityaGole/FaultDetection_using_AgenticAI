"""API-Bank generation, direct evaluation, and extended AgentCoder test stages."""

from __future__ import annotations

import json
import re
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agents.test_executor import BenchmarkExecutor
from config import AppConfig
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import _coerce_api_descriptions, evaluate_api_bank
from llm.client import ChatMessage, LLMEmptyResponseError


PIPELINE_VERSION = 4


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


def _has_unit_evaluator_assertions(source: str) -> bool:
    return bool(
        re.search(r"\bevaluate_api_call\s*\(", source)
        and all(
            re.search(rf"\b{field}\b", source)
            for field in ("parsed_api_name", "api_match", "params_match", "passed")
        )
        and re.search(r"\bassert\b", source)
    )


def _has_property_evaluator_assertions(source: str) -> bool:
    return bool(
        re.search(r"\bevaluate_api_call\s*\(", source)
        and re.search(r"\bpassed\b", source)
        and re.search(r"\bassert\b", source)
    )


def _unit_tests_passed(source: str, section: Any) -> bool:
    has_test = bool(re.search(r"\bdef\s+test_[A-Za-z0-9_]+\s*\(", source))
    return (
        has_test
        and _has_unit_evaluator_assertions(source)
        and section.passed > 0
        and section.failed == 0
    )


def _property_tests_passed(source: str, section: Any) -> bool:
    has_test = bool(
        re.search(r"\bdef\s+test_[A-Za-z0-9_]+\s*\(", source)
        and re.search(r"@given\s*\(", source)
        and _has_property_evaluator_assertions(source)
    )
    return has_test and section.passed > 0 and section.failed == 0


def _make_test_problem(problem: APIBankTurn) -> APIBankTestProblem:
    return APIBankTestProblem(
        task_id=str(problem.task_id),
        entry_point="evaluate_api_call",
        text=(
            "API-Bank evaluates a tool-call string with evaluation.api_bank_evaluator."
            "evaluate_api_bank. It returns APIBankEvaluationResult with fields "
            "passed, parsed_api_name, parsed_params, api_match, params_match, raw_response, "
            "and error. It parses [ApiName(key=value)], compares API names case-insensitively, "
            "requires exact parameters after string normalization, and mock-validates schema "
            "required parameters, types, and supported date formats. The provided "
            "evaluate_api_call(candidate=None, turn=None) invokes that exact repository "
            "evaluator. Unit tests must assert APIBankEvaluationResult attributes, not dict "
            "keys or bool return values. Property tests must be valid executable Hypothesis "
            "tests and assert evaluator results for whitespace transformations that preserve "
            "the original API-name spelling and call. "
            "Do not invent API side effects or test APIs other than the task's expected API."
        ),
    )


def _format_api_call(api_name: str, params: dict[str, Any]) -> str:
    arguments = ", ".join(f"{key}={value!r}" for key, value in params.items())
    return f"[{api_name}({arguments})]"


def _mock_invalid_case(problem: APIBankTurn) -> tuple[APIBankTurn, str] | None:
    registry = _coerce_api_descriptions(problem.api_descriptions)
    api_spec = registry.get(problem.expected_api_name)
    input_params = api_spec.get("input_parameters") if api_spec else None
    if not isinstance(input_params, dict):
        return None

    for name, field_spec in input_params.items():
        if not isinstance(field_spec, dict):
            continue
        expected = dict(problem.expected_param_dict or {})
        if name not in expected:
            continue
        declared_type = str(field_spec.get("type", "")).lower()
        if declared_type == "str":
            invalid_value: Any = 123
        elif declared_type in {"int", "float"}:
            invalid_value = "not-a-number"
        else:
            continue
        expected[name] = invalid_value
        test_turn = APIBankTurn(
            task_id=problem.task_id,
            level=problem.level,
            dialogue_id=problem.dialogue_id,
            turn_id=problem.turn_id,
            api_descriptions=problem.api_descriptions,
            dialogue_history=problem.dialogue_history,
            expected_api_name=problem.expected_api_name,
            expected_param_dict=expected,
            prompt=problem.prompt,
        )
        return test_turn, _format_api_call(problem.expected_api_name, expected)
    return None


def _generate_and_run_tests(
    problem: APIBankTurn,
    generated_api_call: str,
    *,
    config: AppConfig,
) -> tuple[str, dict[str, Any], str, dict[str, Any], dict[str, Any]]:
    test_problem = _make_test_problem(problem)
    turn_json = json.dumps(problem.evaluation_view(), ensure_ascii=False)
    expected_call = _format_api_call(
        problem.expected_api_name,
        problem.expected_param_dict or {},
    )
    wrong_api_call = _format_api_call(
        f"DefinitelyNot{problem.expected_api_name}",
        problem.expected_param_dict or {},
    )
    wrong_params = dict(problem.expected_param_dict or {})
    if wrong_params:
        first_key = next(iter(wrong_params))
        wrong_value = "__different_value_for_test__"
        while str(wrong_value) == str(wrong_params[first_key]):
            wrong_value += "_"
        wrong_params[first_key] = wrong_value
    else:
        wrong_params["unexpected_parameter"] = "__unexpected__"
    wrong_params_call = _format_api_call(problem.expected_api_name, wrong_params)

    mock_case = _mock_invalid_case(problem)
    mock_case_setup = ""
    mock_case_test = ""
    if mock_case is not None:
        invalid_turn_json = json.dumps(mock_case[0].evaluation_view(), ensure_ascii=False)
        mock_case_setup = (
            "\n_mock_invalid_turn = APIBankTurn(**json.loads("
            f"{invalid_turn_json!r}))\n"
            f"_mock_invalid_call = {mock_case[1]!r}\n"
        )
        mock_case_test = (
            "\ndef test_mock_execution_rejects_schema_invalid_value():\n"
            "    result = evaluate_api_call(_mock_invalid_call, turn=_mock_invalid_turn)\n"
            "    assert result.api_match is True\n"
            "    assert result.params_match is True\n"
            "    assert result.passed is False\n"
        )

    implementation = (
        "import json\n"
        "from dataset.api_bank_loader import APIBankTurn\n"
        "from evaluation.api_bank_evaluator import evaluate_api_bank\n\n"
        f"_api_bank_turn = APIBankTurn(**json.loads({turn_json!r}))\n"
        f"_generated_api_call = {generated_api_call!r}\n\n"
        f"_expected_api_call = {expected_call!r}\n"
        f"_wrong_api_call = {wrong_api_call!r}\n"
        f"_wrong_params_call = {wrong_params_call!r}\n"
        f"{mock_case_setup}\n"
        "def api_call():\n"
        "    return _generated_api_call\n\n"
        "def evaluate_api_call(candidate=None, turn=None):\n"
        "    output = api_call() if candidate is None else candidate\n"
        "    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)\n"
    )
    expected_api_name = problem.expected_api_name
    unit_tests = (
        "def test_generated_api_call_matches_task_ground_truth():\n"
        "    result = evaluate_api_call()\n"
        "    assert result.parsed_api_name is not None\n"
        f"    assert result.parsed_api_name.lower() == {expected_api_name.lower()!r}\n"
        "    assert result.api_match is True\n"
        "    assert result.params_match is True\n"
        "    assert result.passed is True\n\n"
        "def test_evaluator_rejects_unparseable_output():\n"
        "    result = evaluate_api_call(candidate='not an API call')\n"
        "    assert result.passed is False\n"
        "    assert result.parsed_api_name is None\n\n"
        "def test_evaluator_rejects_wrong_api_name():\n"
        "    result = evaluate_api_call(candidate=_wrong_api_call)\n"
        "    assert result.api_match is False\n"
        "    assert result.passed is False\n\n"
        "def test_evaluator_api_name_comparison_is_case_insensitive():\n"
        "    candidate = _expected_api_call.replace("
        "_api_bank_turn.expected_api_name, "
        "_api_bank_turn.expected_api_name.swapcase(), 1)\n"
        "    result = evaluate_api_call(candidate=candidate)\n"
        "    assert result.api_match is True\n\n"
        "def test_evaluator_rejects_wrong_parameters():\n"
        "    result = evaluate_api_call(candidate=_wrong_params_call)\n"
        "    assert result.api_match is True\n"
        "    assert result.params_match is False\n"
        "    assert result.passed is False\n"
        f"{mock_case_test}"
    )
    formal_spec = {
        "operations": [
            {
                "operationId": f"OP-{problem.task_id}",
                "operationName": problem.expected_api_name,
                "actionable_sentences": [
                    "The output must contain a parseable API call.",
                    "The API name and parameters must exactly match the task ground truth.",
                    "The call must pass mock schema validation in the API-Bank evaluator.",
                ],
                "lifted_nl": [
                    "When the generated call satisfies the expected API name, parameters, "
                    "and schema, the canonical API-Bank evaluator returns passed=True."
                ],
                "LABEL": "API_BANK_EVALUATOR_CONTRACT",
                "Precondition": "The candidate must be a string representing a parseable API call.",
                "Function": "evaluate_api_bank(turn, generated_output)",
                "Postcondition": (
                    "The result passes only when the parsed API name matches case-insensitively, "
                    "the normalized parameters exactly match, and mock schema execution succeeds."
                ),
                "assumptions": [],
                "invariants": [
                    "Malformed calls, API-name mismatches, parameter mismatches, or mock schema "
                    "failures do not pass."
                ],
            }
        ]
    }
    property_tests = (
        "from hypothesis import given, strategies as st, settings\n\n"
        "@given(prefix=st.text(alphabet=' \\t\\r\\n', max_size=8), "
        "suffix=st.text(alphabet=' \\t\\r\\n', max_size=8))\n"
        "@settings(max_examples=20, deadline=1500)\n"
        "def test_evaluator_result_is_invariant_to_surrounding_whitespace(prefix, suffix):\n"
        "    baseline = evaluate_api_call()\n"
        "    transformed = evaluate_api_call(candidate=prefix + api_call() + suffix)\n"
        "    assert transformed.passed is baseline.passed\n"
        "    assert transformed.api_match is baseline.api_match\n"
        "    assert transformed.params_match is baseline.params_match\n\n"
        "@given(prefix=st.text(alphabet=' \\t\\r\\n', max_size=8), "
        "suffix=st.text(alphabet=' \\t\\r\\n', max_size=8))\n"
        "@settings(max_examples=20, deadline=1500)\n"
        "def test_expected_call_passes_with_surrounding_whitespace(prefix, suffix):\n"
        "    result = evaluate_api_call(candidate=prefix + _expected_api_call + suffix)\n"
        "    assert result.api_match is True\n"
        "    assert result.params_match is True\n"
        "    assert result.passed is True\n"
    )
    report = BenchmarkExecutor(timeout_seconds=config.test_timeout_seconds).execute(
        implementation=implementation,
        unit_tests=unit_tests,
        property_tests=property_tests,
        entry_point=test_problem.entry_point,
        python_paths=(Path(__file__).resolve().parent,),
    )
    report_data = report.to_dict()
    has_unit_tests = bool(re.search(r"\bdef\s+test_[A-Za-z0-9_]+\s*\(", unit_tests))
    has_property_tests = bool(
        re.search(r"\bdef\s+test_[A-Za-z0-9_]+\s*\(", property_tests)
        and re.search(r"@given\s*\(", property_tests)
    )
    unit_checks_evaluator = _has_unit_evaluator_assertions(unit_tests)
    property_checks_evaluator = _has_property_evaluator_assertions(property_tests)
    unit_passed = _unit_tests_passed(unit_tests, report.unit_tests)
    property_passed = _property_tests_passed(property_tests, report.property_tests)
    return (
        implementation,
        formal_spec,
        unit_tests,
        property_tests,
        {
            "report": report_data,
            "unit_tests_passed": unit_passed,
            "property_tests_passed": property_passed,
            "test_validation_errors": [
                *([] if has_unit_tests else ["No executable unit test function was generated."]),
                *(
                    []
                    if unit_checks_evaluator
                    else ["Unit tests do not assert the canonical API-Bank evaluator fields."]
                ),
                *(
                    []
                    if has_property_tests
                    else ["No Hypothesis property test using @given was generated."]
                ),
                *(
                    []
                    if property_checks_evaluator
                    else ["Property tests do not assert the canonical API-Bank evaluator result."]
                ),
            ],
        },
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
    generation_error: str | None = None
    request_failed = False
    empty_provider_response = False
    try:
        if cached_call is None:
            generated_api_call = limited_client.chat(
                messages=[
                    ChatMessage(
                        role="system",
                        content=(
                            "You are an API-calling assistant. Determine the next API call "
                            "from the supplied API documentation and dialogue. Return only "
                            "one call in the requested format; do not write Python code or explanation."
                        ),
                    ),
                    ChatMessage(role="user", content=problem.prompt),
                ],
                model=model,
                temperature=0,
                max_tokens=512,
                retries=3,
            )
        else:
            generated_api_call = cached_call
    except Exception as exc:
        generated_api_call = ""
        generation_error = f"{type(exc).__name__}: {exc}"
        request_failed = True
        empty_provider_response = isinstance(exc, LLMEmptyResponseError)

    generated_api_call = generated_api_call.strip()
    empty_response = not generated_api_call
    evaluation = evaluate_api_bank(problem, generated_api_call)
    api_call_status = (
        "empty_response"
        if empty_provider_response or (empty_response and not request_failed)
        else "request_failed"
        if request_failed
        else "valid"
        if evaluation.passed
        else "invalid"
    )
    try:
        implementation, formal_spec, unit_tests, property_tests, test_results = (
            _generate_and_run_tests(
                problem,
                generated_api_call,
                config=config,
            )
        )
    except Exception as exc:
        return {
            "pipeline_version": PIPELINE_VERSION,
            "task_id": problem.task_id,
            "pipeline_status": "failed",
            "api_call_source": call_source,
            "api_call_status": api_call_status,
            "request_status": "failed" if empty_response else call_source,
            "failure_stage": "test_execution",
            "generated_api_call": generated_api_call,
            "evaluation": {
                "passed": False,
                "parsed_api_name": evaluation.parsed_api_name,
                "parsed_params": evaluation.parsed_params,
                "api_match": evaluation.api_match,
                "params_match": evaluation.params_match,
                "unit_tests_passed": False,
                "property_tests_passed": False,
                "error": f"Test generation/execution failed: {type(exc).__name__}: {exc}",
            },
        }

    unit_passed = test_results["unit_tests_passed"]
    property_passed = test_results["property_tests_passed"]
    passed = evaluation.passed and unit_passed and property_passed
    error = generation_error or evaluation.error
    if error is None and not unit_passed:
        error = "Generated unit tests failed"
    if error is None and not property_passed:
        error = "Generated property tests failed"
    return {
        "pipeline_version": PIPELINE_VERSION,
        "task_id": problem.task_id,
        "pipeline_status": "incomplete" if empty_response or request_failed else "completed",
        "api_call_source": call_source,
        "api_call_status": api_call_status,
        "request_status": (
            "failed"
            if empty_response or request_failed
            else "reused"
            if call_source == "reused"
            else "success"
        ),
        "failure_stage": "api_call_generation" if empty_response or request_failed else None,
        "generated_api_call": generated_api_call,
        "generated_code": implementation,
        "formal_spec": formal_spec,
        "unit_tests": unit_tests,
        "property_tests": property_tests,
        "test_execution_report": test_results["report"],
        "evaluation": {
            "passed": passed,
            "parsed_api_name": evaluation.parsed_api_name,
            "parsed_params": evaluation.parsed_params,
            "api_match": evaluation.api_match,
            "params_match": evaluation.params_match,
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
            "mode": "extended_api_call",
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
