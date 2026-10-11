import argparse
import json
import os
from collections import Counter
from pathlib import Path

import openai
from datasets import load_dataset
from dotenv import load_dotenv
from gradio_client import Client, handle_file
from tqdm import tqdm

load_dotenv()
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
openai.api_key = os.getenv("OPENAI_API_KEY")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OPENAI_MODEL", "")
REQUEST_TIMEOUT = int(os.getenv("OPENAI_REQUEST_TIMEOUT", "30"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2048"))
EVALUATOR_URL = "https://bigcode-bigcodebench-evaluator.hf.space/"


def clean_solution(text):
    text = (text or "").strip()
    if text.startswith("```python"):
        text = text[len("```python"):]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def generate_solution(task):
    prompt = (
        "Solve this BigCodeBench programming task. Return the complete, executable "
        "Python solution, including required imports and the requested function. "
        "Return code only, with no Markdown fences or explanation.\n\n"
        + task["instruct_prompt"]
    )
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            stream=False,
            max_tokens=MAX_TOKENS,
            request_timeout=REQUEST_TIMEOUT,
            messages=[
                {"role": "system", "content": "Return only complete executable Python code."},
                {"role": "user", "content": prompt},
            ],
        )
        choice = response.choices[0]
        solution = clean_solution(choice["message"].get("content"))
        if not solution:
            return "", "empty", "The model returned no message content"
        if choice.get("finish_reason") == "length":
            return solution, "truncated", "The response reached the output token limit"
        return solution, "success", ""
    except Exception as exc:
        return "", "failed", repr(exc)


def load_tasks(limit):
    tasks = list(load_dataset("bigcode/bigcodebench", split="v0.1.4"))
    return tasks[:limit] if limit else tasks


def generate_samples(tasks):
    samples = []
    for index, task in enumerate(tqdm(tasks, desc="BigCodeBench generation")):
        solution, status, error = generate_solution(task)
        samples.append(
            {
                "task_id": task["task_id"],
                "solution": solution,
                "_identifier": str(index),
                "agent_request_status": status,
                "agent_error": error,
            }
        )
    return samples


def evaluate_samples(samples, split, parallel):
    sample_path = PROJECT_ROOT / "dataset" / f"bigcodebench_{split}_agent_samples.jsonl"
    with open(sample_path, "w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")

    task_ids = [sample["task_id"].split("/", 1)[-1] for sample in samples]
    client = Client(EVALUATOR_URL)
    remote_results, pass_at_k = client.predict(
        split=split,
        subset="full",
        samples=handle_file(str(sample_path)),
        pass_k="1",
        parallel=parallel,
        min_time_limit=1,
        max_as_limit=30 * 1024,
        max_data_limit=30 * 1024,
        max_stack_limit=10,
        calibrated=False,
        check_gt_only=False,
        no_gt=False,
        selective_evaluate=",".join(task_ids),
        api_name="/predict",
    )

    results_by_task = remote_results.get("eval", {})
    passed = 0
    evaluated = 0
    task_evaluations = {}
    for task_results in results_by_task.values():
        for task_result in task_results:
            evaluated += 1
            if task_result.get("status") == "pass":
                passed += 1
            task_evaluations[task_result["task_id"]] = task_result

    summary = {
        "benchmark": "BigCodeBench",
        "split": split,
        "model": MODEL,
        "count": len(samples),
        "evaluated": evaluated,
        "passed": passed,
        "accuracy": passed / evaluated if evaluated else 0,
        "pass_at_1": pass_at_k.get("pass@1"),
        "groundtruth_pass_rate": pass_at_k.get("gt_pass_rate"),
        "request_status": dict(Counter(sample["agent_request_status"] for sample in samples)),
    }

    task_output = PROJECT_ROOT / "dataset" / f"bigcodebench_{split}_agent_results.json"
    summary_output = PROJECT_ROOT / "dataset" / f"bigcodebench_{split}_agent_summary.json"
    raw_output = PROJECT_ROOT / "dataset" / f"bigcodebench_{split}_official_evaluator_results.json"
    with open(task_output, "w", encoding="utf-8") as handle:
        merged_results = [
            {
                **sample,
                "evaluation": task_evaluations.get(sample["task_id"]),
            }
            for sample in samples
        ]
        json.dump(merged_results, handle, indent=2, ensure_ascii=False)
    with open(summary_output, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
    with open(raw_output, "w", encoding="utf-8") as handle:
        json.dump({"results": remote_results, "pass_at_k": pass_at_k}, handle, indent=2, ensure_ascii=False)

    print(json.dumps(summary, indent=2))
    print(f"Saved generated samples to {sample_path}")
    print(f"Saved task results to {task_output}")
    print(f"Saved summary to {summary_output}")
    print(f"Saved official evaluator output to {raw_output}")


def main():
    parser = argparse.ArgumentParser(description="Run AgentCoder on BigCodeBench Instruct.")
    parser.add_argument("--limit", type=int, default=0, help="Run only the first N tasks; 0 means all 1140.")
    parser.add_argument("--parallel", type=int, default=4, help="Parallelism used by the official hosted evaluator.")
    parser.add_argument("--reuse-samples", type=Path, help="Evaluate an existing JSONL samples file without model calls.")
    args = parser.parse_args()
    split = "instruct"

    if args.reuse_samples:
        samples = [json.loads(line) for line in args.reuse_samples.read_text(encoding="utf-8").splitlines() if line.strip()]
        if args.limit:
            samples = samples[:args.limit]
    else:
        if not MODEL:
            parser.error("Set OPENAI_MODEL in .env before generating BigCodeBench samples.")
        tasks = load_tasks(args.limit)
        samples = generate_samples(tasks)

    evaluate_samples(samples, split, args.parallel)


if __name__ == "__main__":
    main()
