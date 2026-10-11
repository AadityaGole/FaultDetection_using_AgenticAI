# AgentCoder Benchmark Comparison

## 1. Objective

This report evaluates the AgentCoder workflow on four different benchmark types:

- **MBPP**: Python function generation and unit-test execution.
- **DS-1000**: Data-science code generation across seven Python libraries.
- **BigCodeBench**: practical Python tasks with diverse library/function calls.
- **API-Bank**: Tool/API-call generation from multi-turn conversations.

Fresh generations use the OpenAI-compatible provider configured in `.env`. The API-Bank results below are the latest saved run with local mock checks enabled. MBPP and DS-1000 numbers are earlier runs and are not a controlled same-model comparison.

<!-- ## 2. AgentCoder Workflow

```mermaid
flowchart LR
    A[Benchmark task] --> B[Programmer agent]
    B --> C[Generated solution or API call]
    C --> D[Benchmark evaluator]
    D --> E[Pass/fail and error]
    E --> F[Saved task result and summary]
    F --> G[Optional repair round]
    G --> B
``` -->

The experiment measures both model quality and operational reliability. A failed API request is different from a generated answer that executes but fails the benchmark tests.

## 3. Results At A Glance

| Benchmark | Evaluation unit | Tasks / turns | Exact-match passed | Exact-match accuracy | Local mock passed | Mock accuracy among checked | Result file |
|---|---|---:|---:|---:|---:|---:|---|
| MBPP, stored answers | Python task | 257 | 230 | 89.5% | N/A | N/A | `dataset/mbpp_existing_evaluation.json` |
| MBPP, fresh AgentCoder | Python task | 257 | 129* | 50.2%* | N/A | N/A | `dataset/mbpp_agent_evaluation.json` |
| DS-1000 | Data-science task | 1,000 | 19 | 1.9% | N/A | N/A | `dataset/ds1000_agent_results.json` |
| BigCodeBench Instruct | Python task | 1,140 | 125 | 11.0% | N/A | N/A | `dataset/bigcodebench_instruct_agent_summary.json` |
| API-Bank level 1 | API-call turn | 389 | 216 | 55.5% | 232 / 287 | 80.8% | `dataset/api_bank_level_1_agent_results_mock.json` |
| API-Bank level 2 | API-call turn | 119 | 34 | 28.6% | 38 / 52 | 73.1% | `dataset/api_bank_level_2_agent_results_mock.json` |

### MBPP Baseline Note

The original stored MBPP metadata reports `229/257`, while a fresh local execution of the stored completions reports `230/257`. The prior AgentCoder run reported `129/257`, but that result predates the fix that prevents old completions from being counted when generation fails.

\* The previous fresh AgentCoder MBPP score was contaminated by stored completions when model requests failed. The executor has now been corrected to clear historical completions before generation. Rerun the MBPP benchmark before using the fresh-generation score in a final comparison.

## 4. MBPP

### What It Tests

MBPP tests short Python programming tasks with assertions. The evaluator writes the generated function and its test assertions to a temporary Python file and executes it in a subprocess.

### AgentCoder Result

- Fresh tasks sent to the programmer agent: `257`
- Successful generated responses: `105`
- Empty responses: `41`
- Failed requests: `111`
- Prior reported fresh solutions passing tests: `129/257` (provisional; rerun after the accounting fix)

### Interpretation

MBPP is the strongest of the three fresh-generation results because tasks are short and test cases are direct. The result is still constrained by Kilo free-model timeouts and empty responses. The stored historical answers are not a fair comparison to fresh generation because they were produced by a different model/run.

## 5. DS-1000

### What It Tests

DS-1000 contains 1,000 data-science tasks involving Matplotlib, NumPy, Pandas, PyTorch, SciPy, scikit-learn, and TensorFlow. Each record includes an executable `code_context` containing the official test logic.

### Overall Result

- Tasks: `1,000`
- Successful model requests: `510`
- Failed model requests: `490`
- Passed: `19/1,000`
- Overall accuracy: `1.9%`

### Results By Library

| Library | Tasks | Passed | Accuracy |
|---|---:|---:|---:|
| Matplotlib | 155 | 0 | 0.0% |
| NumPy | 220 | 8 | 3.6% |
| Pandas | 291 | 11 | 3.8% |
| PyTorch | 68 | 0 | 0.0% |
| SciPy | 106 | 0 | 0.0% |
| scikit-learn | 115 | 0 | 0.0% |
| TensorFlow | 45 | 0 | 0.0% |

### Interpretation

DS-1000 is substantially harder than MBPP because prompts are longer, solutions depend on library-specific behavior, and execution requires a scientific Python environment. The free model also failed nearly half of requests, so the measured score combines model quality with provider reliability.

## 6. BigCodeBench

### What It Tests

BigCodeBench evaluates practical Python tasks with complex instructions and diverse function/library calls. This runner uses the official `v0.1.4` Instruct split and submits generated samples to BigCodeBench's hosted evaluator, which executes the benchmark's task-specific `unittest` tests.

### Full-Run Result

- Tasks evaluated: `1,140`
- Passed: `125/1,140`
- Pass@1: `11.0%`
- Model request statuses: `206` success, `775` empty, `99` truncated, `60` failed
- Ground-truth evaluator pass rate: `99.65%` (`1,136/1,140`)

The ground-truth evaluator pass rate measures whether BigCodeBench's own reference solutions pass its tests; it is an evaluator-health check, not AgentCoder accuracy. Empty model responses cannot solve their tasks and are counted as failures in the overall score.

Artifacts:

- Generated samples: `dataset/bigcodebench_instruct_agent_samples.jsonl`
- Per-task output and evaluation details: `dataset/bigcodebench_instruct_agent_results.json`
- Summary: `dataset/bigcodebench_instruct_agent_summary.json`
- Raw official evaluator output: `dataset/bigcodebench_instruct_official_evaluator_results.json`

## 7. API-Bank

### What It Tests

API-Bank evaluates whether an agent can select the correct API and produce the correct parameters from a multi-turn conversation. The runner parses outputs in the form:

```text
[ApiName(key='value')]
```

The result is compared with the official API name and parameter dictionary.

### Results

The runner reports two different pass metrics:

- **Exact-match accuracy** compares the parsed API name and parameters with the dataset's expected call, over every turn.
- **Mock accuracy** runs parseable calls against API-Bank's local mock implementations and applies the mock's task-specific correctness checker. It is divided only by `mock_checked`, not by all turns.

| Split | Turns | Exact-match passes | Exact-match accuracy | Request statuses | Mock checked | Mock passes | Mock accuracy among checked |
|---|---:|---:|---:|---|---:|---:|---:|
| Level 1 | 389 | 216 | 55.5% | 324 success, 48 empty, 6 truncated, 11 failed | 287 (73.8% coverage) | 232 | 80.8% |
| Level 2 | 119 | 34 | 28.6% | 73 success, 41 empty, 2 truncated, 3 failed | 52 (43.7% coverage) | 38 | 73.1% |

Mock statuses not included in `mock_checked` are `not_parseable`, `invalid_call`, `failed`, `skipped_external`, or `unavailable_dependency`. They are not counted as mock passes or mock failures because the official per-API correctness method did not complete.

### Interpretation

The mock accuracy is higher than exact-match accuracy because the official API-Bank checker can accept semantically valid calls that differ textually from the recorded call. These conditional mock scores cover only calls the local mock could execute. Level 2 has lower mock coverage, so its `73.1%` should not be compared directly to level 1 without also considering coverage.

## 8. Cross-Benchmark Comparison

| Dimension | MBPP | DS-1000 | BigCodeBench | API-Bank |
|---|---|---|---|---|
| Primary capability | Function coding | Library-aware data science coding | Practical function generation with diverse libraries | Tool/API usage |
| Output format | Python code | Python solution fragment | Complete Python solution | Structured API call |
| Evaluation | Assertions | Official executable test context | Official hosted task-specific tests | Exact call plus local mock checks |
| Main difficulty | Algorithm correctness | Library knowledge and runtime state | Complex instructions and function interactions | Planning and schema adherence |
| Fresh AgentCoder result | Prior result: 50.2%* | 1.9% (earlier run) | 11.0% (1,140 tasks) | Exact: 55.5% level 1; 28.6% level 2 |
| Main operational risk | Empty/failed requests | Long prompts, heavy libraries, timeouts | Empty output and remote evaluator availability | Long dialogues and provider failures |

## 9. Main Findings

1. **AgentCoder is most effective on compact, directly testable code tasks.** MBPP produced the highest fresh-generation accuracy.
2. **Data-science generation is the hardest workload.** DS-1000 requires both code synthesis and correct use of specialized libraries.
3. **API use is a different capability from code generation.** API-Bank needs structured output and correct tool arguments, not just executable Python.
4. **Provider reliability materially affects the scores.** Empty, truncated, and failed requests are reported separately from incorrect generated calls.
5. **The benchmark evaluator must match the task type.** Python subprocess execution is appropriate for MBPP and DS-1000; API-Bank needs structured API-call scoring.

## 10. Limitations

- The benchmark runs were collected at different times and may use different providers/models; consult the `.env` and saved run artifacts before treating cross-benchmark comparisons as controlled.
- MBPP stored-answer results were created by earlier model runs and are not a controlled baseline against the current Kilo model.
- API-Bank exact-match accuracy and local-mock accuracy are distinct metrics. Mock accuracy excludes calls that could not be parsed, executed, or checked.
- DS-1000 execution depends on installed library versions and machine capabilities, especially for TensorFlow, PyTorch, and plotting tasks.
- BigCodeBench's full run had a high empty-response rate (`775/1,140`), which depresses overall accuracy; report request reliability alongside pass@1.
- Generated code is executed locally. Use an isolated environment or sandbox for untrusted model output.

## 11. Reproduction Commands

Run fresh MBPP AgentCoder generation and evaluation:

```powershell
cd Vanilla_Method/AgentCoder/src
python .\test_executor_mbpp.py
```

Run DS-1000 on all tasks:

```powershell
python .\run_ds1000.py
```

Run a smaller DS-1000 test first:

```powershell
python .\run_ds1000.py --limit 10 --timeout 120
```

Run API-Bank level 1:

```powershell
python .\run_api_bank.py --level 1
```

Run API-Bank level 2:

```powershell
python .\run_api_bank.py --level 2
```

Run a small BigCodeBench smoke test:

```powershell
python .\run_bigcodebench.py --limit 5
```

Run all 1,140 BigCodeBench Instruct tasks:

```powershell
python .\run_bigcodebench.py
```

Run only the existing MBPP answers without Kilo:

```powershell
python .\test_executor_mbpp.py --offline
```

## 12. Conclusion

AgentCoder now has runners for four benchmark families. The full BigCodeBench Instruct run passed `125/1,140` tasks (`11.0%` pass@1), with `775` empty model responses. MBPP's fresh score remains provisional, and DS-1000/API-Bank results came from earlier runs. Full evaluations with the same provider and model are needed for a controlled cross-benchmark comparison.
