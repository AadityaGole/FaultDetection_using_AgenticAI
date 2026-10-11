# BigCodeBench-Instruct Integration

## Summary

The Agent Coder pipeline now supports **BigCodeBench-Instruct** (v0.1.4 split), a large-scale code generation benchmark with 1140 tasks using unittest-based evaluation.

## Changes Made

### 1. Dataset Loader: `dataset/bigcodebench_loader.py` (NEW)

**Class: `BigCodeBenchProblem`**
- Frozen dataclass with fields:
  - `task_id`: Unique task identifier (string)
  - `instruct_prompt`: Natural language instruction for code generation
  - `complete_prompt`: Full docstring variant
  - `canonical_solution`: Ground truth implementation
  - `test`: unittest.TestCase class code
  - `entry_point`: Function name (default: "task_func")
  - `doc_struct`: Parsed JSON metadata (dict or None)
  - `libs`: List of required libraries (list or None)
  
- **Methods:**
  - `.generation_view()`: Returns fields needed for code generation (task_id, instruct_prompt, entry_point, libs)
  - `.evaluation_view()`: Returns fields needed for evaluation (canonical_solution, test)

**Function: `load_bigcodebench()`**
- Loads from Hugging Face "bigcode/bigcodebench" dataset
- Default split: "v0.1.4" (1140 tasks)
- Fallback to local JSON files if not cached
- Uses `_parse_jsonish()` helper to handle JSON string fields (doc_struct, libs)

### 2. Evaluator: `evaluation/bigcodebench_evaluator.py` (NEW)

**Class: `BigCodeBenchEvaluationResult`**
- Frozen dataclass with:
  - `passed`: bool (test verdict)
  - `stdout`: str (test output)
  - `stderr`: str (error/exception info)
  - `returncode`: int or None (process exit code)
  - `timed_out`: bool (execution timeout flag)

**Function: `build_bigcodebench_eval_code()`**
- Concatenates:
  1. `import unittest` header
  2. Candidate implementation code
  3. Test code from problem
  4. `unittest.main()` runner
- Returns a complete executable Python file

**Function: `evaluate_bigcodebench()`**
- **Execution flow:**
  1. Build eval code (implementation + tests + runner)
  2. Write to temp file
  3. Execute with `subprocess.run(timeout=30)`
  4. Capture stdout/stderr as strings
  5. Report pass/fail based on returncode (0 = pass)
  
- **Error handling:**
  - Timeout: Catches `subprocess.TimeoutExpired`, forces stdout/stderr to strings, returns `timed_out=True`
  - Bytes conversion: Handles both string and bytes output (defensive for different Python versions)
  - All returned fields are guaranteed strings (no bytes) for JSON serialization

### 3. CLI Integration: `main.py` (MODIFIED)

**Dataset name variants:**
- Accepts: `bigcodebench`, `bigcodebench-instruct`, `bigcodebench_instruct`, `bigcodebend-instruct` (typo-tolerant)
- All normalized to: `bigcodebench_instruct` internally

**Load path:**
```python
if d_name == "bigcodebench_instruct":
    return load_bigcodebench(
        split=args.split or "v0.1.4",
        limit=args.limit,
        start=args.start,
        end=args.end,
        task_id=task_id_arg if isinstance(task_id_arg, int) else None,
        local_path=config.dataset_local_path or None,
    )
```

**Evaluation path:**
```python
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
```

### 4. Module Exports: Updated `__init__.py` files

**`dataset/__init__.py`**: Exports `BigCodeBenchProblem`, `load_bigcodebench`

**`evaluation/__init__.py`**: Exports `BigCodeBenchEvaluationResult`, `evaluate_bigcodebench`, `parse_unittest_output`

### 5. Tests: `tests/test_core.py` (ADDED 2 NEW TESTS)

**`test_bigcodebench_loader_reads_instruct_prompt()`**
- Verifies loader correctly extracts `instruct_prompt`, `entry_point`, `libs` from dataset sample
- Validates JSON parsing for `doc_struct` (from string to dict)

**`test_bigcodebench_evaluator_runs_builtin_tests()`**
- Correct code: Verifies unittest evaluation passes on valid implementation
- Wrong code: Verifies evaluation fails when implementation returns incorrect value
- Validates both `passed` flag and `stderr` error messages

All 14 tests passing:
```bash
$ pytest tests/test_core.py -v
tests/test_core.py::test_loader_sanitizes_generation_payload PASSED
tests/test_core.py::test_mbpp_entry_point_auto_deduction PASSED
tests/test_core.py::test_artifact_manager_creates_expected_structure PASSED
tests/test_core.py::test_default_config_is_kilo_only PASSED
tests/test_core.py::test_build_llm_client_requires_kilo_api_key PASSED
tests/test_core.py::test_problem_object_keeps_evaluation_payload PASSED
tests/test_core.py::test_ds1000_problem_views PASSED
tests/test_core.py::test_api_bank_call_parser PASSED
tests/test_core.py::test_benchmark_table_generation PASSED
tests/test_core.py::test_formal_spec_normalization_and_validation PASSED
tests/test_core.py::test_api_bank_requires_mock_execution_success PASSED
tests/test_core.py::test_executor_reports_property_syntax_error PASSED
tests/test_core.py::test_bigcodebench_loader_reads_instruct_prompt PASSED
tests/test_core.py::test_bigcodebench_evaluator_runs_builtin_tests PASSED
============================== 14 passed in 1.91s
```

## Bug Fix: JSON Serialization

**Issue**: `Object of type bytes is not JSON serializable` during evaluation result serialization

**Root Cause**: In `evaluate_bigcodebench()`, when `subprocess.TimeoutExpired` occurs, the `exc.stdout` and `exc.stderr` attributes may be bytes instead of strings (depending on Python version/platform handling of `text=True` mode).

**Fix**: Added defensive type checking in timeout handler:
```python
stdout_str = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout.decode("utf-8", errors="replace") if exc.stdout else "")
stderr_str = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else "Execution timed out")
```

**Validation**: All subprocess output fields now guaranteed to be strings before JSON serialization.

## Usage

### Single Task
```bash
PYTHONPATH=. python main.py --dataset bigcodebench-instruct --limit 1 --mode extended
```

### Multiple Tasks
```bash
PYTHONPATH=. python main.py --dataset bigcodebench_instruct --limit 10 --mode extended
```

### Custom Split
```bash
PYTHONPATH=. python main.py --dataset bigcodebench-instruct --split v0.1.4 --limit 50
```

### Baseline Mode (Without Property Tests)
```bash
PYTHONPATH=. python main.py --dataset bigcodebench-instruct --limit 10 --mode baseline
```

## Output Structure

Each task generates:
```
runs/bigcodebench_instruct/BigCodeBench/{task_id}/
├── problem.json
├── iteration_0/
│   ├── requirement_analysis.json
│   ├── implementation/
│   │   └── implementation.py
│   ├── unit_tests/
│   │   └── unit_tests.py
│   ├── property_tests/
│   │   └── property_tests.py
│   ├── formal_specification/
│   │   ├── formal_spec.json
│   │   ├── formal_spec_artifacts.json
│   │   └── refinements.json (if extended mode)
│   └── execution_results.json
└── final/
    ├── solution.py
    └── evaluation_results.json
```

## Dataset Specifications

**Source**: Hugging Face `bigcode/bigcodebench` dataset

| Property | Value |
|----------|-------|
| Total Tasks | 1,140 |
| Split | v0.1.4 (default: bigcodebench) |
| Test Format | unittest.TestCase classes |
| Entry Point | task_func (customizable) |
| Time Limit | 30 seconds (per task) |
| Libraries | Dynamically listed in problem.libs |

## Pipeline Integration

BigCodeBench integrates seamlessly with the existing 4-benchmark pipeline:

```
Pipeline
├── MBPP (257 tasks) - Python entry point extraction
├── DS-1000 (1000 tasks) - Code context requirement
├── API-Bank (399 tasks) - Mock API execution with date validation
└── BigCodeBench (1140 tasks) - Unittest-based evaluation  ← NEW
```

## Performance Notes

- **Loader**: ~0.5s per task (Hugging Face cache)
- **LLM Generation**: ~50s per task (5 API calls: requirements, code, unit tests, formal spec, property tests)
- **Test Execution**: ~5s per task (unittest runner)
- **Total per task**: ~55s (extended mode)

## Compatibility

- Python: 3.8+
- Dataset source: Hugging Face `bigcode/bigcodebench` v0.1.4 split
- Test framework: unittest (built-in)
- Dependencies: No new external packages required

## Known Limitations

1. **Property tests**: Generated by Hypothesis-based property test agent; may have syntax errors in extended mode (caught by pre-flight validation)
2. **Timeout handling**: 30-second hardcoded limit (configurable via `evaluate_bigcodebench(..., timeout_seconds=N)`)
3. **Library imports**: Assumes all required libraries are pre-installed in environment

## Related Changes

This BigCodeBench integration builds on previous pipeline improvements:
- Mode-aware evaluation (`include_property_tests` parameter)
- Pre-flight syntax validation (catches invalid Hypothesis code before execution)
- All four datasets now cached-backed via Hugging Face
