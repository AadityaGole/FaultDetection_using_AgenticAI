import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from datasets import load_dataset
from dotenv import load_dotenv
import openai
from tqdm import tqdm

load_dotenv()
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
openai.api_key = os.getenv("OPENAI_API_KEY")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OPENAI_MODEL", "liquid/lfm-2.5-2.6b:free")
TIMEOUT = int(os.getenv("OPENAI_REQUEST_TIMEOUT", "15"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1024"))


def clean_completion(text):
    text = text or ""
    text = text.replace("```python", "").replace("```", "")
    text = text.split("END SOLUTION")[0]
    return text.strip()


def generate_solution(sample):
    prompt = (
        "Complete the DS-1000 Python task below. Return only the Python code "
        "that should replace the solution placeholder. Do not explain your reasoning.\n\n"
        + sample["prompt"]
    )
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            stream=False,
            max_tokens=MAX_TOKENS,
            request_timeout=TIMEOUT,
            messages=[
                {"role": "system", "content": "Return only executable Python code."},
                {"role": "user", "content": prompt},
            ],
        )
        text = response.choices[0]["message"].get("content") or ""
        return clean_completion(text), "success", ""
    except Exception as exc:
        return "", "failed", repr(exc)


def execute_solution(sample, solution, timeout):
    program = (
        sample["code_context"]
        + "\ncode = "
        + repr(solution)
        + "\ntest_execution(code)\n"
        + ("test_string(code)\n" if "test_string(" in sample["code_context"] else "")
    )
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".py", dir=PROJECT_ROOT / "tmp", delete=False
    ) as handle:
        handle.write(program)
        path = handle.name
    try:
        result = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, timeout=timeout
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output or "passed"
    except subprocess.TimeoutExpired:
        return False, "timed out"
    finally:
        Path(path).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Run AgentCoder on DS-1000.")
    parser.add_argument("--limit", type=int, default=0, help="Run only the first N tasks; 0 means all 1000.")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    (PROJECT_ROOT / "tmp").mkdir(exist_ok=True)

    samples = list(load_dataset("xlangai/DS-1000", split="test"))
    if args.limit:
        samples = samples[: args.limit]
    results = []
    for index, sample in enumerate(tqdm(samples, desc="DS-1000")):
        solution, status, error = generate_solution(sample)
        passed, execution_result = (False, "no generated solution")
        if solution:
            passed, execution_result = execute_solution(sample, solution, args.timeout)
        results.append(
            {
                "index": index,
                "problem_id": sample["metadata"]["problem_id"],
                "library": sample["metadata"]["library"],
                "prompt": sample["prompt"],
                "generated_solution": solution,
                "agent_request_status": status,
                "agent_error": error,
                "passed": passed,
                "result": execution_result,
            }
        )

    output_path = PROJECT_ROOT / "dataset" / "ds1000_agent_results.json"
    summary_path = PROJECT_ROOT / "dataset" / "ds1000_agent_summary.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    by_library = {}
    for library in sorted({item["library"] for item in results}):
        group = [item for item in results if item["library"] == library]
        by_library[library] = {"count": len(group), "passed": sum(item["passed"] for item in group), "accuracy": sum(item["passed"] for item in group) / len(group)}
    summary = {"count": len(results), "passed": sum(item["passed"] for item in results), "accuracy": sum(item["passed"] for item in results) / len(results) if results else 0, "by_library": by_library, "request_status": dict(Counter(item["agent_request_status"] for item in results))}
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"Saved task results to {output_path}")
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
