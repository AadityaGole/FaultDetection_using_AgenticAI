from __future__ import annotations

import json
from pathlib import Path

import pytest

from config import AppConfig
from dataset.api_bank_loader import APIBankTurn
from dataset.bigcodebench_loader import BigCodeBenchProblem, load_bigcodebench
from dataset.ds1000_loader import DS1000Problem
from dataset.mbpp_loader import MBPPProblem, load_mbpp, sanitize_for_generation
from evaluation.api_bank_evaluator import evaluate_api_bank, parse_api_call
from evaluation.bigcodebench_evaluator import evaluate_bigcodebench, parse_unittest_output
from agents.test_executor import BenchmarkExecutor
from llm.client import LLMClientError, build_llm_client
from utils.artifact_manager import ArtifactManager


def test_loader_sanitizes_generation_payload(tmp_path: Path):
    payload = [
        {
            "task_id": 7,
            "text": "Return the sum of two numbers.",
            "entry_point": "add",
            "code": "def add(a, b): return a + b",
            "test_list": ["assert add(1, 2) == 3"],
            "challenge_test_list": ["assert add(2, 2) == 4"],
        }
    ]
    local = tmp_path / "mbpp.json"
    local.write_text(json.dumps(payload), encoding="utf-8")

    problems = load_mbpp(local_path=str(local))
    assert len(problems) == 1
    sanitized = sanitize_for_generation(problems[0])
    assert sanitized == {"task_id": 7, "text": "Return the sum of two numbers.", "entry_point": "add"}
    assert problems[0].evaluation_view()["code"] == "def add(a, b): return a + b"


def test_mbpp_entry_point_auto_deduction(tmp_path: Path):
    payload = [
        {
            "task_id": 11,
            "text": "Write a python function to remove occurrences of a character.",
            # Note: No 'entry_point' field!
            "code": "def remove_Occ(s, ch): return s.replace(ch, '')",
            "test_list": ["assert remove_Occ('hellolloll', 'l') == 'helollol'"],
        }
    ]
    local = tmp_path / "mbpp_missing_entry_point.json"
    local.write_text(json.dumps(payload), encoding="utf-8")

    problems = load_mbpp(local_path=str(local))
    assert len(problems) == 1
    assert problems[0].entry_point == "remove_Occ"


def test_artifact_manager_creates_expected_structure(tmp_path: Path):
    manager = ArtifactManager(tmp_path, dataset_name="mbpp")
    paths = manager.iteration_paths(42, 0)
    assert paths.iteration_dir.exists()
    assert paths.formal_spec_dir.exists()
    assert paths.unit_tests_dir.exists()
    assert paths.property_tests_dir.exists()
    assert paths.final_dir.exists()


def test_default_config_is_kilo_only():
    config = AppConfig()
    assert config.provider == "kilo"
    assert config.kilo_base_url == "https://api.kilo.ai/api/gateway"
    assert "liquid/lfm-2.5-2.6b:free" in config.kilo_model



def test_build_llm_client_requires_kilo_api_key():
    config = AppConfig(provider="kilo", kilo_api_key="")
    with pytest.raises(LLMClientError, match="KILO_API_KEY"):
        build_llm_client(config)


def test_problem_object_keeps_evaluation_payload():
    problem = MBPPProblem(task_id=3, text="Return the larger of two numbers.", entry_point="max2")
    assert problem.generation_view() == {"task_id": 3, "text": "Return the larger of two numbers.", "entry_point": "max2"}
    assert problem.evaluation_view()["task_id"] == 3


def test_ds1000_problem_views():
    ds_prob = DS1000Problem(task_id=1, prompt="Calculate sum", code_context="test()", lib="NumPy")
    assert ds_prob.generation_view()["lib"] == "NumPy"
    assert ds_prob.text == "Calculate sum"
    assert ds_prob.evaluation_view()["code_context"] == "test()"


def test_api_bank_call_parser():
    text = "[SearchEngine(query='machine learning', limit=5)]"
    api_name, params = parse_api_call(text)
    assert api_name == "SearchEngine"
    assert params == {"query": "machine learning", "limit": 5}


def test_benchmark_table_generation(tmp_path: Path):
    from generate_benchmark_table import generate_main_table, generate_ds1000_library_table

    mbpp_dir = tmp_path / "mbpp"
    mbpp_dir.mkdir(parents=True)
    summary = {
        "dataset": "mbpp",
        "total": 10,
        "passed": 8,
        "accuracy": "80.00%",
        "successful_requests": 10,
        "failed_requests": 0,
    }
    (mbpp_dir / "run_summary.json").write_text(json.dumps(summary), encoding="utf-8")

    table = generate_main_table(tmp_path)
    assert "80.00%" in table
    assert "Vanilla AgentCoder" in table
    assert "Extended AgentCoder 2.0" in table

    ds_table = generate_ds1000_library_table(tmp_path)
    assert "NumPy" in ds_table
    assert "Pandas" in ds_table


def test_formal_spec_normalization_and_validation():
    from formal_spec.pipeline import normalize_formal_spec, _validate_formal_spec

    # 1. Test flat dictionary auto-wrapping (MBPP)
    mbpp_prob = MBPPProblem(task_id=1, text="Find max in list", entry_point="find_max")
    flat_spec = {
        "operationId": "OP-1",
        "operationName": "find_max",
        "actionable_sentences": ["Find max in list"],
        "lifted_nl": ["whenever find_max is called it returns the maximum element"],
        "LABEL": "FUNCTIONAL_SPEC",
        "Precondition": "isinstance(arr, list) and len(arr) > 0 and all(isinstance(x, int) for x in arr)",
        "Function": "find_max(arr: List[int]) -> int",
        "Postcondition": "result in arr and all(result >= x for x in arr)",
    }
    normalized = normalize_formal_spec(flat_spec, problem=mbpp_prob)
    assert "operations" in normalized
    assert len(normalized["operations"]) == 1
    assert _validate_formal_spec(mbpp_prob, normalized) == []

    # 2. Test API-Bank formal spec
    api_turn = APIBankTurn(
        task_id="turn_1",
        level=1,
        dialogue_id="diag_1",
        turn_id=0,
        api_descriptions="AddAlarm",
        dialogue_history=[],
        expected_api_name="AddAlarm",
        expected_param_dict={"time": "2023-09-12 14:00:00"},
        prompt="Schedule an alarm",
    )
    api_spec = {
        "operations": [
            {
                "operationId": "OP-ALARM",
                "operationName": "AddAlarm",
                "LABEL": "TOOL_CALL",
                "Precondition": "authenticated(user_token) and valid_iso_time(time)",
                "Function": "AddAlarm(token: str, time: str) -> status: str",
                "Postcondition": "alarm_registered(time) and status == 'success'",
            }
        ]
    }
    norm_api = normalize_formal_spec(api_spec, problem=api_turn)
    assert _validate_formal_spec(api_turn, norm_api) == []
    # Verify metadata was backfilled
    assert len(norm_api["operations"][0]["actionable_sentences"]) > 0

    # 3. Test DS-1000 formal spec
    ds_prob = DS1000Problem(task_id=10, prompt="Shuffle df by List", code_context="", lib="Pandas")
    ds_spec = {
        "operations": [
            {
                "operationId": "OP-DS10",
                "operationName": "shuffle_df",
                "LABEL": "DATA_TRANSFORM",
                "Precondition": "is_dataframe(df) and 'Type' in df.columns and len(List) == len(df)",
                "Function": "shuffle_df(df: pd.DataFrame, List: np.ndarray) -> int",
                "Postcondition": "0 <= result <= len(df) and result == count_type_changes(df, List)",
            }
        ]
    }
    norm_ds = normalize_formal_spec(ds_spec, problem=ds_prob)
    assert _validate_formal_spec(ds_prob, norm_ds) == []

    # 4. Verify rejection of generic placeholder specifications
    generic_spec = {
        "operations": [
            {
                "operationId": "OP-GEN",
                "operationName": "foo",
                "actionable_sentences": ["do something"],
                "lifted_nl": ["do it"],
                "LABEL": "FUNCTIONAL_SPEC",
                "Precondition": "inputs satisfy the problem statement",
                "Function": "foo(...) -> Any",
                "Postcondition": "the result satisfies the task description",
            }
        ]
    }
    errors = _validate_formal_spec(mbpp_prob, generic_spec)
    assert len(errors) >= 2
    assert any("generic or empty Precondition" in err for err in errors)
    assert any("generic or empty Postcondition" in err for err in errors)


def test_api_bank_requires_mock_execution_success():
    turn = APIBankTurn(
        task_id="turn_1",
        level=1,
        dialogue_id="diag_1",
        turn_id=0,
        api_descriptions=[
            {
                "name": "ModifyRegistration",
                "input_parameters": {
                    "appointment_id": {"type": "str"},
                    "new_appointment_date": {"type": "str"},
                    "new_appointment_doctor": {"type": "str"},
                },
            }
        ],
        dialogue_history=[],
        expected_api_name="ModifyRegistration",
        expected_param_dict={
            "appointment_id": "34567890",
            "new_appointment_date": "2023-03-26",
            "new_appointment_doctor": "Dr. Lee",
        },
        prompt="Modify appointment",
    )

    ok = evaluate_api_bank(turn, "[ModifyRegistration(appointment_id='34567890', new_appointment_date='2023-03-26', new_appointment_doctor='Dr. Lee')]")
    assert ok.passed is True

    bad = evaluate_api_bank(turn, "[ModifyRegistration(appointment_id='34567890', new_appointment_date='03/26/2023', new_appointment_doctor='Dr. Lee')]")
    assert bad.passed is False
    assert bad.error in {"Parameter mismatch", "API call failed mock execution"}


def test_executor_reports_property_syntax_error():
    executor = BenchmarkExecutor(timeout_seconds=5)
    report = executor.execute(
        implementation="def foo():\n    return 1\n",
        unit_tests="assert foo() == 1\n",
        property_tests="def test_bad(:\n    pass\n",
        entry_point="foo",
    )

    assert report.unit_tests.passed == 1
    assert report.property_tests.failed == 1
    assert any("SyntaxError" in err for err in report.runtime_errors)


def test_bigcodebench_loader_reads_instruct_prompt(tmp_path: Path):
    payload = [
        {
            "task_id": "BigCodeBench/0",
            "complete_prompt": "Complete prompt",
            "instruct_prompt": "Write a function that returns 1.",
            "canonical_solution": "def task_func():\n    return 1",
            "code_prompt": "def task_func():\n    pass",
            "test": "import unittest\nclass TestCases(unittest.TestCase):\n    def test_one(self):\n        self.assertEqual(task_func(), 1)\n",
            "entry_point": "task_func",
            "doc_struct": "{\"description\": [\"Return 1\"], \"returns\": [\"int\"]}",
            "libs": "['unittest']",
        }
    ]
    local = tmp_path / "bigcodebench.json"
    local.write_text(json.dumps(payload), encoding="utf-8")

    problems = load_bigcodebench(local_path=str(local))
    assert len(problems) == 1
    assert problems[0].text == "Write a function that returns 1."
    assert problems[0].entry_point == "task_func"
    assert problems[0].libs == ["unittest"]


def test_bigcodebench_evaluator_runs_builtin_tests(tmp_path: Path):
    problem = BigCodeBenchProblem(
        task_id="BigCodeBench/0",
        instruct_prompt="Return 1.",
        complete_prompt="",
        code_prompt="",
        canonical_solution="def task_func():\n    return 1",
        test="import unittest\nclass TestCases(unittest.TestCase):\n    def test_one(self):\n        self.assertEqual(task_func(), 1)\n",
        entry_point="task_func",
        doc_struct={"description": ["Return 1"]},
        libs=["unittest"],
    )

    ok = evaluate_bigcodebench(problem, "def task_func():\n    return 1\n", timeout_seconds=5)
    assert ok.passed is True
    assert ok.passed_tests == 1
    assert ok.total_tests == 1

    bad = evaluate_bigcodebench(problem, "def task_func():\n    return 2\n", timeout_seconds=5)
    assert bad.passed is False
    assert bad.passed_tests == 0
    assert bad.total_tests == 1


def test_parse_unittest_output_counts():
    total, passed = parse_unittest_output("Ran 10 tests in 5.345s\n\nOK\n")
    assert total == 10
    assert passed == 10

    total, passed = parse_unittest_output("Ran 10 tests in 4.629s\n\nFAILED (errors=8)\n")
    assert total == 10
    assert passed == 2

    total, passed = parse_unittest_output("Ran 10 tests\n\nFAILED (failures=3, errors=2)\n")
    assert total == 10
    assert passed == 5

    total, passed = parse_unittest_output("Ran 10 tests\n\nFAILED (failures=10)\n")
    assert total == 10
    assert passed == 0

    total, passed = parse_unittest_output("SyntaxError: invalid syntax")
    assert total == 0
    assert passed == 0


def test_executor_parses_unittest_counts_for_unit_and_property_tests():
    executor = BenchmarkExecutor(timeout_seconds=5)
    unit_tests = """
def test_u1(): assert task_func(1) == 2
def test_u2(): assert task_func(2) == 4
def test_u3(): assert task_func(3) == 0  # should fail
"""
    property_tests = """
from hypothesis import given, strategies as st, settings

@settings(max_examples=10)
@given(st.integers(min_value=-100, max_value=100))
def test_p1(x):
    assert task_func(x) == x * 2

@settings(max_examples=10)
@given(st.integers(min_value=1, max_value=100))
def test_p2(x):
    assert task_func(x) > 0

@settings(max_examples=10)
@given(st.integers(min_value=-100, max_value=100))
def test_p3(x):
    assert task_func(x) < 0  # will fail for positive x
"""
    implementation = "def task_func(x): return x * 2\n"

    report = executor.execute(
        implementation=implementation,
        unit_tests=unit_tests,
        property_tests=property_tests,
        entry_point="task_func",
    )

    assert report.unit_tests.passed == 2
    assert report.unit_tests.failed == 1
    assert report.property_tests.passed == 2
    assert report.property_tests.failed == 1


def test_bigcodebench_evaluate_problem_test_counts():
    from main import evaluate_problem

    problem = BigCodeBenchProblem(
        task_id="BigCodeBench/0",
        instruct_prompt="Return 1.",
        complete_prompt="",
        code_prompt="",
        canonical_solution="def task_func():\n    return 1",
        test="import unittest\nclass TestCases(unittest.TestCase):\n    def test_one(self):\n        self.assertEqual(task_func(), 1)\n    def test_two(self):\n        self.assertEqual(task_func(), 1)\n",
        entry_point="task_func",
        doc_struct={"description": ["Return 1"]},
        libs=["unittest"],
    )

    # Without test_report, extracts passed count from ground-truth unittest stderr
    eval_dict = evaluate_problem("bigcodebench_instruct", problem, "def task_func():\n    return 1\n", timeout_seconds=5)
    assert eval_dict["passed"] is True
    assert eval_dict["unit_tests_passed"] == 2
    assert eval_dict["property_tests_passed"] == 0

    # With test_report, extracts passed counts for both unit and property based tests
    executor = BenchmarkExecutor(timeout_seconds=5)
    report = executor.execute(
        implementation="def task_func():\n    return 1\n",
        unit_tests="def test_u1(): assert task_func() == 1\ndef test_u2(): assert task_func() == 1\ndef test_u3(): assert task_func() == 1\n",
        property_tests="from hypothesis import given, strategies as st, settings\n@settings(max_examples=10)\n@given(st.integers())\ndef test_p1(x): assert task_func() == 1\n",
        entry_point="task_func",
    )
    eval_dict_with_report = evaluate_problem(
        "bigcodebench_instruct",
        problem,
        "def task_func():\n    return 1\n",
        timeout_seconds=5,
        test_report=report,
        include_property_tests=True,
    )
    assert eval_dict_with_report["passed"] is True
    assert eval_dict_with_report["unit_tests_passed"] == 3
    assert eval_dict_with_report["property_tests_passed"] == 1
