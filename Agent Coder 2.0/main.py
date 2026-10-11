"""CLI entry point for baseline and extended AgentCoder runs across MBPP, DS-1000, and API-Bank."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agents.programmer_agent import ProgrammerAgent
from agents.property_test_agent import PropertyTestAgent
from agents.requirement_analyzer import RequirementAnalyzer
from agents.test_executor import BenchmarkExecutor
from agents.unit_test_agent import UnitTestAgent
from config import AppConfig
from dataset.api_bank_loader import load_api_bank
from dataset.bigcodebench_loader import load_bigcodebench
from dataset.ds1000_loader import load_ds1000
from dataset.mbpp_loader import load_mbpp, sanitize_for_generation
from evaluation.api_bank_evaluator import evaluate_api_bank
from evaluation.bigcodebench_evaluator import evaluate_bigcodebench, parse_unittest_output
from evaluation.ds1000_evaluator import evaluate_ds1000
from evaluation.evaluator import evaluate_mbpp
from formal_spec.adapter import FormalSpecAdapter
from llm.client import build_llm_client
from utils.artifact_manager import ArtifactManager
from utils.logging_utils import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extended AgentCoder benchmark runner with Formal Spec & PBT")
    parser.add_argument(
        "--dataset",
        choices=[
            "mbpp",
            "ds1000",
            "api_bank",
            "api-bank",
            "bigcodebench",
            "bigcodebench-instruct",
            "bigcodebench_instruct",
            "bigcodebend-instruct",
        ],
        default="mbpp",
    )
    parser.add_argument("--split", default="test")
    parser.add_argument("--level", type=int, default=1, help="API-Bank level (1 or 2)")
    parser.add_argument("--lib", default="", help="DS-1000 library filter (e.g. numpy, pandas)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start", type=int, default=None)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--mode", choices=["baseline", "extended"], default="extended")
    parser.add_argument("--max-iterations", type=int, default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--formal-spec-model", default=None)
    parser.add_argument("--unit-test-model", default=None)
    parser.add_argument("--property-test-model", default=None)
    parser.add_argument("--code-generation-model", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--test-timeout-seconds", type=int, default=None)
    parser.add_argument("--resume", action="store_true", help="Resume from previously evaluated tasks")
    return parser.parse_args()


def _override_config(base: AppConfig, args: argparse.Namespace) -> AppConfig:
    raw_name = args.dataset.replace("-", "_")
    if raw_name in {"bigcodebench", "bigcodebench_instruct", "bigcodebend_instruct"}:
        d_name = "bigcodebench_instruct"
    else:
        d_name = raw_name
    artifact_root = f"api_bank_level_{args.level}" if d_name == "api_bank" else d_name
    return AppConfig(
        provider=args.provider or base.provider,
        kilo_base_url=base.kilo_base_url,
        kilo_api_key=base.kilo_api_key,
        kilo_model=base.kilo_model,
        model=args.model or base.model,
        code_generation_model=args.code_generation_model or base.code_generation_model,
        formal_spec_model=args.formal_spec_model or base.formal_spec_model,
        unit_test_model=args.unit_test_model or base.unit_test_model,
        property_test_model=args.property_test_model or base.property_test_model,
        max_iterations=args.max_iterations or base.max_iterations,
        test_timeout_seconds=args.test_timeout_seconds or base.test_timeout_seconds,
        output_dir=Path(args.output_dir) if args.output_dir else base.output_dir,
        dataset_name=d_name,
        dataset_split=args.split or base.dataset_split,
        dataset_level=args.level,
        dataset_lib=args.lib or base.dataset_lib,
        dataset_local_path=base.dataset_local_path,
        property_strategy=base.property_strategy,
        generation_retries=base.generation_retries,
        formal_spec_retries=base.formal_spec_retries,
        test_generation_retries=base.test_generation_retries,
        artifact_root_name=artifact_root,
    )


def build_feedback(report: dict[str, Any], *, iteration: int, stage: str) -> dict[str, Any]:
    return {
        "iteration": iteration,
        "stage": stage,
        "summary": "test execution finished with failures",
        "report": report,
    }


def parse_unittest_output(stderr: str) -> tuple[int, int]:
    """Parse unittest output to extract total tests and passed count.
    
    Parses output like:
    - "Ran 10 tests in 5.345s\n\nOK" -> (10, 10)
    - "Ran 10 tests in 4.629s\n\nFAILED (errors=8)" -> (10, 2)
    - "Ran 10 tests\n\nFAILED (failures=3, errors=2)" -> (10, 5)
    
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



def evaluate_problem(
    dataset_name: str,
    problem: Any,
    code: str,
    timeout_seconds: int,
    test_report: Any | None = None,
    include_property_tests: bool = False,
) -> dict[str, Any]:
    """Dispatch benchmark evaluation according to problem type."""
    if dataset_name == "mbpp":
        res = evaluate_mbpp(problem, code, timeout_seconds=timeout_seconds)
        return {
            "passed": res.passed,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "returncode": res.returncode,
            "timed_out": res.timed_out,
        }
    elif dataset_name == "ds1000":
        res = evaluate_ds1000(problem, code, timeout_seconds=timeout_seconds)
        return {
            "passed": res.passed,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "returncode": res.returncode,
            "timed_out": res.timed_out,
        }
    elif dataset_name == "bigcodebench_instruct":
        res = evaluate_bigcodebench(problem, code, timeout_seconds=timeout_seconds)
        unit_tests_passed = 0
        property_tests_passed = 0
        if test_report is not None:
            if getattr(test_report, "unit_tests", None) is not None:
                ut = test_report.unit_tests
                ut_stderr = getattr(ut, "stderr", "") or (ut.failures[0].get("stderr", "") if ut.failures else "")
                if ut_stderr:
                    total_ut, passed_ut = parse_unittest_output(ut_stderr)
                    unit_tests_passed = passed_ut if total_ut > 0 else ut.passed
                else:
                    unit_tests_passed = ut.passed
            if getattr(test_report, "property_tests", None) is not None:
                pt = test_report.property_tests
                pt_stderr = getattr(pt, "stderr", "") or (pt.failures[0].get("stderr", "") if pt.failures else "")
                if pt_stderr:
                    total_pt, passed_pt = parse_unittest_output(pt_stderr)
                    property_tests_passed = passed_pt if total_pt > 0 else pt.passed
                else:
                    property_tests_passed = pt.passed
        else:
            total_res, passed_res = parse_unittest_output(res.stderr)
            unit_tests_passed = passed_res if total_res > 0 else getattr(res, "passed_tests", (1 if res.passed else 0))

        return {
            "passed": res.passed,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "returncode": res.returncode,
            "timed_out": res.timed_out,
            "unit_tests_passed": unit_tests_passed,
            "property_tests_passed": property_tests_passed,
        }
    elif dataset_name == "api_bank":
        res = evaluate_api_bank(problem, code)
        unit_tests_passed = False
        property_tests_passed = None
        if test_report is not None:
            unit_tests_passed = getattr(test_report, "unit_tests", None) is not None and test_report.unit_tests.passed == 1
            if getattr(test_report, "property_tests", None) is not None:
                property_tests_passed = test_report.property_tests.passed == 1
        tests_passed = bool(unit_tests_passed and (property_tests_passed if include_property_tests else True))
        final_passed = bool(res.passed and tests_passed)
        return {
            "passed": final_passed,
            "parsed_api_name": res.parsed_api_name,
            "parsed_params": res.parsed_params,
            "api_match": res.api_match,
            "params_match": res.params_match,
            "unit_tests_passed": unit_tests_passed,
            "property_tests_passed": property_tests_passed,
            "property_tests_required": include_property_tests,
            "error": None if final_passed else (res.error or "API call or tests did not pass"),
        }
    return {"passed": False, "error": f"Unknown dataset {dataset_name}"}


def run_single_task(problem: Any, config: AppConfig, artifact_manager: ArtifactManager, client, mode: str, resume: bool = False) -> dict[str, Any]:
    logger = setup_logging()
    task_id = getattr(problem, "task_id", 0)
    problem_dir = artifact_manager.task_dir(task_id)

    if resume and (problem_dir / "final" / "evaluation_results.json").exists():
        try:
            eval_dict = json.loads((problem_dir / "final" / "evaluation_results.json").read_text(encoding="utf-8"))
            final_code = ""
            if (problem_dir / "final" / "solution.py").exists():
                final_code = (problem_dir / "final" / "solution.py").read_text(encoding="utf-8")
            paths = artifact_manager.iteration_paths(task_id, 0)
            test_exec = {}
            if (paths.iteration_dir / "execution_results.json").exists():
                test_exec = json.loads((paths.iteration_dir / "execution_results.json").read_text(encoding="utf-8"))
            logger.info("Resuming task %s from existing evaluation (passed=%s)", task_id, eval_dict.get("passed"))
            return {
                "task_id": task_id,
                "mode": mode,
                "request_status": "success" if "error" not in eval_dict else "failed",
                "test_execution_report": test_exec,
                "evaluation": eval_dict,
                "final_code": final_code,
            }
        except Exception:
            pass

    logger.info("Running task %s in %s mode (dataset: %s)", task_id, mode, config.dataset_name)

    requirement_analyzer = RequirementAnalyzer(client=client, model=config.resolve_model("code_generation"))
    programmer = ProgrammerAgent(client=client, model=config.resolve_model("code_generation"))
    unit_test_agent = UnitTestAgent(client=client, model=config.resolve_model("unit_test"))
    property_test_agent = PropertyTestAgent(client=client, model=config.resolve_model("property_test"))
    executor = BenchmarkExecutor(timeout_seconds=config.test_timeout_seconds)
    formal_spec_adapter = FormalSpecAdapter(client=client, config=config)

    generation_payload = problem.generation_view() if hasattr(problem, "generation_view") else sanitize_for_generation(problem)
    artifact_manager.write_json(problem_dir / "problem.json", generation_payload)

    formal_spec_result = None
    current_code = ""
    initial_report = None
    final_report = None
    feedback_payload = None

    try:
        paths = artifact_manager.iteration_paths(task_id, 0)

        # 1. System + User Prompt (Requirement Analysis)
        analysis = requirement_analyzer.analyze(problem)
        artifact_manager.write_json(paths.iteration_dir / "requirement_analysis.json", asdict(analysis))

        # 2. Code Generation (Implementation)
        code_result = programmer.generate(
            problem,
            analysis,
            previous_code=None,
            feedback=None,
        )
        current_code = code_result.code
        artifact_manager.write_text(paths.iteration_dir / "generated_code.py", current_code)

        # 3. Branching into Testing Tracks:
        # Track A: Unit Test Generator (Testing II)
        unit_tests = unit_test_agent.generate(
            problem,
            implementation_code=current_code,
            requirements_summary=analysis.summary,
        )
        unit_tests_code = unit_tests.code
        artifact_manager.write_text(paths.unit_tests_dir / "unit_tests.py", unit_tests_code)
        artifact_manager.write_json(paths.unit_tests_dir / "unit_tests_meta.json", {"model": unit_tests.model})

        # Track B: Formal Specification Generation (Testing I) -> Property Based Test Generator (Testing II)
        property_tests_code = ""
        formal_spec_result = None
        if mode == "extended":
            formal_spec_result = formal_spec_adapter.generate(problem, model=config.resolve_model("formal_spec"))
            artifact_manager.write_json(paths.formal_spec_dir / "formal_spec.json", formal_spec_result.formal_spec)
            artifact_manager.write_json(paths.formal_spec_dir / "formal_spec_artifacts.json", {
                "validation_status": formal_spec_result.validation_status,
                "validation_errors": formal_spec_result.result.artifacts.validation_errors,
                "refinement_attempts": formal_spec_result.result.artifacts.refinement_attempts,
            })

            property_tests = property_test_agent.generate(problem, formal_spec_result.formal_spec)
            property_tests_code = property_tests.code
            artifact_manager.write_text(paths.property_tests_dir / "property_tests.py", property_tests_code)
            artifact_manager.write_json(paths.property_tests_dir / "property_tests_meta.json", {"model": property_tests.model})
        else:
            artifact_manager.write_text(paths.property_tests_dir / "property_tests.py", "")

        # 4. Test Execution (Testing III)
        report = executor.execute(
            implementation=current_code,
            unit_tests=unit_tests_code,
            property_tests=property_tests_code if mode == "extended" else None,
            entry_point=getattr(problem, "entry_point", None),
        )
        report_dict = report.to_dict()
        artifact_manager.write_json(paths.iteration_dir / "execution_results.json", report_dict)

        # 5. Final Benchmark Evaluation against Ground Truth (No loop back)
        evaluation_dict = evaluate_problem(
            config.dataset_name,
            problem,
            current_code,
            timeout_seconds=config.test_timeout_seconds,
            test_report=report,
            include_property_tests=(mode == "extended"),
        )
        artifact_manager.write_text(problem_dir / "final" / "solution.py", current_code)
        artifact_manager.write_json(problem_dir / "final" / "evaluation_results.json", evaluation_dict)

        return {
            "task_id": task_id,
            "mode": mode,
            "request_status": "success",
            "test_execution_report": report_dict,
            "evaluation": evaluation_dict,
            "final_code": current_code,
        }

    except Exception as exc:
        logger.warning("Task %s request failure: %s", task_id, exc)
        eval_fail = {"passed": False, "error": str(exc)}
        artifact_manager.write_json(problem_dir / "final" / "evaluation_results.json", eval_fail)
        return {
            "task_id": task_id,
            "mode": mode,
            "request_status": "failed",
            "error": str(exc),
            "initial_report": None,
            "final_report": None,
            "evaluation": eval_fail,
            "iterations": 0,
            "final_code": "",
        }



def load_dataset_by_name(config: AppConfig, args: argparse.Namespace) -> list[Any]:
    d_name = config.dataset_name.lower()
    task_id_arg = None
    if args.task_id is not None:
        try:
            task_id_arg = int(args.task_id)
        except ValueError:
            task_id_arg = args.task_id

    if d_name == "mbpp":
        return load_mbpp(
            split=args.split,
            limit=args.limit,
            start=args.start,
            end=args.end,
            task_id=task_id_arg if isinstance(task_id_arg, int) else None,
            local_path=config.dataset_local_path or None,
        )
    elif d_name == "ds1000":
        return load_ds1000(
            split=args.split,
            limit=args.limit,
            start=args.start,
            end=args.end,
            task_id=task_id_arg if isinstance(task_id_arg, int) else None,
            lib=args.lib or None,
            local_path=config.dataset_local_path or None,
        )
    elif d_name == "bigcodebench_instruct":
        bigcode_split = args.split if args.split and args.split != "test" else "v0.1.4"
        return load_bigcodebench(
            split=bigcode_split,
            limit=args.limit,
            start=args.start,
            end=args.end,
            task_id=str(task_id_arg) if task_id_arg is not None else None,
            local_path=config.dataset_local_path or None,
        )
    elif d_name == "api_bank":
        return load_api_bank(
            level=args.level,
            split=args.split,
            limit=args.limit,
            start=args.start,
            end=args.end,
            task_id=task_id_arg,
            local_path=config.dataset_local_path or None,
        )
    raise ValueError(f"Unknown dataset: {d_name}")


def main() -> None:
    args = parse_args()
    base_config = AppConfig()
    config = _override_config(base_config, args)

    client = build_llm_client(config)
    artifact_manager = ArtifactManager(config.output_dir, dataset_name=config.artifact_root_name)

    problems = load_dataset_by_name(config, args)
    print(f"Loaded {len(problems)} tasks from {config.dataset_name} ({args.mode} mode)")

    results: list[dict[str, Any]] = []
    passed_count = 0
    total = len(problems)
    successful_requests = 0
    failed_requests = 0
    accuracy = 0.0
    summary_path = artifact_manager.root / "run_summary.json"

    if not problems:
        print(f"No tasks found to run for {config.dataset_name}.")
        return

    for idx, problem in enumerate(problems, start=1):
        task_id = getattr(problem, "task_id", idx)
        res = run_single_task(problem, config, artifact_manager, client, args.mode, resume=args.resume)
        results.append(res)
        is_passed = bool(res.get("evaluation", {}).get("passed"))
        if is_passed:
            passed_count += 1

        total = len(results)
        successful_requests = sum(1 for r in results if r.get("request_status") == "success")
        failed_requests = sum(1 for r in results if r.get("request_status") == "failed")
        accuracy = (passed_count / total * 100.0) if total > 0 else 0.0

        summary_payload = {
            "dataset": config.dataset_name,
            "mode": args.mode,
            "total": total,
            "passed": passed_count,
            "accuracy": f"{accuracy:.2f}%",
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "results": results,
        }
        summary_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        status_str = "PASSED" if is_passed else "FAILED"
        print(f"[{idx}/{len(problems)}] Task {task_id}: {status_str} | Current: {passed_count}/{total} ({accuracy:.1f}%) | Req Success: {successful_requests}, Failed: {failed_requests}")

    print(
        f"\nRun completed! Passed: {passed_count}/{total} ({accuracy:.2f}%). "
        f"Successful requests: {successful_requests}, Failed requests: {failed_requests}. "
        f"Summary saved to {summary_path}"
    )



if __name__ == "__main__":
    main()
