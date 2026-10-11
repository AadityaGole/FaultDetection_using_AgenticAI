"""Script to generate the head-to-head benchmark comparison table from the runs/ directory."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict


# Vanilla baseline numbers from Aaditya Gole's benchmark
VANILLA_BASELINE: dict[str, dict[str, Any]] = {
    "mbpp": {
        "benchmark": "MBPP",
        "eval_unit": "Python task",
        "total_tasks": 257,
        "passed": 129,
        "accuracy": "50.2%",
        "successful_requests": 105,
        "failed_requests": 152,
        "result_file": "dataset/mbpp_agent_evaluation.json",
    },
    "ds1000": {
        "benchmark": "DS-1000",
        "eval_unit": "Data-science task",
        "total_tasks": 1000,
        "passed": 19,
        "accuracy": "1.9%",
        "successful_requests": 510,
        "failed_requests": 490,
        "result_file": "dataset/ds1000_agent_results.json",
    },
    "api_bank_level_1": {
        "benchmark": "API-Bank (L1)",
        "eval_unit": "API-call turn",
        "total_tasks": 389,
        "passed": 28,
        "accuracy": "7.2%",
        "successful_requests": 282,
        "failed_requests": 107,
        "result_file": "dataset/api_bank_level_1_agent_results.json",
    },
    "api_bank_level_2": {
        "benchmark": "API-Bank (L2)",
        "eval_unit": "API-call turn",
        "total_tasks": 119,
        "passed": 18,
        "accuracy": "15.1%",
        "successful_requests": 82,
        "failed_requests": 37,
        "result_file": "dataset/api_bank_level_2_agent_results.json",
    },
}

VANILLA_DS1000_LIBS: dict[str, dict[str, Any]] = {
    "numpy": {"name": "NumPy", "tasks": 220, "passed": 8, "accuracy": "3.6%"},
    "pandas": {"name": "Pandas", "tasks": 291, "passed": 11, "accuracy": "3.8%"},
    "pytorch": {"name": "PyTorch", "tasks": 68, "passed": 0, "accuracy": "0.0%"},
    "scipy": {"name": "SciPy", "tasks": 106, "passed": 0, "accuracy": "0.0%"},
    "sklearn": {"name": "Scikit-Learn", "tasks": 115, "passed": 0, "accuracy": "0.0%"},
    "matplotlib": {"name": "Matplotlib", "tasks": 155, "passed": 0, "accuracy": "0.0%"},
    "tensorflow": {"name": "TensorFlow", "tasks": 45, "passed": 0, "accuracy": "0.0%"},
}


def normalize_lib(lib: str) -> str:
    cleaned = lib.lower().replace("-", "").replace("_", "")
    if cleaned in ("sklearn", "scikitlearn"):
        return "sklearn"
    if cleaned in ("tensorflow", "tf"):
        return "tensorflow"
    if cleaned in ("matplotlib", "plt"):
        return "matplotlib"
    if cleaned in ("pytorch", "torch"):
        return "pytorch"
    return cleaned


def collect_benchmark_stats(benchmark_dir: Path) -> dict[str, Any]:
    """Parse run_summary.json or scan task directories to compute stats."""
    summary_file = benchmark_dir / "run_summary.json"
    if summary_file.exists():
        try:
            data = json.loads(summary_file.read_text(encoding="utf-8"))
            return {
                "total": data.get("total", 0),
                "passed": data.get("passed", 0),
                "accuracy": data.get("accuracy", "0.00%"),
                "successful_requests": data.get("successful_requests", 0),
                "failed_requests": data.get("failed_requests", 0),
                "source": str(summary_file),
            }
        except Exception:
            pass

    # Fallback scan of directories
    total = 0
    passed = 0
    success_req = 0
    failed_req = 0
    if benchmark_dir.exists():
        for task_dir in benchmark_dir.iterdir():
            if not task_dir.is_dir():
                continue
            eval_file = task_dir / "final" / "evaluation_results.json"
            if eval_file.exists():
                total += 1
                try:
                    eval_data = json.loads(eval_file.read_text(encoding="utf-8"))
                    if eval_data.get("passed"):
                        passed += 1
                    if "error" in eval_data and not eval_data.get("stdout"):
                        failed_req += 1
                    else:
                        success_req += 1
                except Exception:
                    failed_req += 1

    acc = (passed / total * 100.0) if total > 0 else 0.0
    return {
        "total": total,
        "passed": passed,
        "accuracy": f"{acc:.2f}%",
        "successful_requests": success_req,
        "failed_requests": failed_req,
        "source": str(benchmark_dir),
    }


def collect_ds1000_library_stats(ds1000_dir: Path) -> dict[str, dict[str, int]]:
    """Scan ds1000 run directory to group results by library."""
    lib_stats: dict[str, dict[str, int]] = {
        k: {"total": 0, "passed": 0} for k in VANILLA_DS1000_LIBS
    }

    if not ds1000_dir.exists():
        return lib_stats

    for task_dir in ds1000_dir.iterdir():
        if not task_dir.is_dir():
            continue
        prob_file = task_dir / "problem.json"
        eval_file = task_dir / "final" / "evaluation_results.json"
        if not prob_file.exists() or not eval_file.exists():
            continue

        try:
            prob_data = json.loads(prob_file.read_text(encoding="utf-8"))
            eval_data = json.loads(eval_file.read_text(encoding="utf-8"))
            raw_lib = prob_data.get("lib", "unknown")
            norm_lib = normalize_lib(raw_lib)
            if norm_lib in lib_stats:
                lib_stats[norm_lib]["total"] += 1
                if eval_data.get("passed"):
                    lib_stats[norm_lib]["passed"] += 1
        except Exception:
            continue

    return lib_stats


def generate_main_table(runs_dir: Path) -> str:
    """Generate the main comparison table (Section 3)."""
    rows = []
    benchmarks = [
        ("mbpp", "MBPP", "runs/mbpp"),
        ("ds1000", "DS-1000", "runs/ds1000"),
        ("api_bank_level_1", "API-Bank (L1)", "runs/api_bank_level_1"),
        ("api_bank_level_2", "API-Bank (L2)", "runs/api_bank_level_2"),
    ]

    header = (
        "| Benchmark | Method | Evaluation Unit | Tasks Evaluated | Passed | Overall Accuracy | "
        "Successful Requests | Request Failures | Result File |\n"
        "|:---|:---|:---:|---:|---:|---:|---:|---:|:---|"
    )
    rows.append(header)

    for key, name, run_rel_path in benchmarks:
        vanilla = VANILLA_BASELINE[key]
        extended = collect_benchmark_stats(runs_dir / key)

        # Vanilla row
        v_total = f"{vanilla['total_tasks']:,}" if isinstance(vanilla['total_tasks'], int) else str(vanilla['total_tasks'])
        rows.append(
            f"| **{name}** | Vanilla AgentCoder | {vanilla['eval_unit']} | {v_total} | "
            f"{vanilla['passed']} | {vanilla['accuracy']} | {vanilla['successful_requests']} | "
            f"{vanilla['failed_requests']} | `{vanilla['result_file']}` |"
        )

        # Extended row
        ext_total = f"{extended['total']}/{vanilla['total_tasks']}" if extended['total'] < vanilla['total_tasks'] else f"{extended['total']:,}"
        rows.append(
            f"| **{name}** | **Extended AgentCoder 2.0 (Ours)** | {vanilla['eval_unit']} | "
            f"**{ext_total}** | **{extended['passed']}** | **{extended['accuracy']}** | "
            f"{extended['successful_requests']} | {extended['failed_requests']} | "
            f"`{run_rel_path}/run_summary.json` |"
        )

    return "\n".join(rows)


def generate_ds1000_library_table(runs_dir: Path) -> str:
    """Generate the DS-1000 per-library breakdown table (Section 5)."""
    lib_stats = collect_ds1000_library_stats(runs_dir / "ds1000")

    header = (
        "| Library | Total Tasks | Evaluated | Vanilla Passed | Vanilla Acc | "
        "Extended Passed | Extended Acc |\n"
        "|:---|---:|---:|---:|---:|---:|---:|"
    )
    rows = [header]

    total_tasks = 0
    total_eval = 0
    total_v_passed = 0
    total_ext_passed = 0

    for norm_key, info in VANILLA_DS1000_LIBS.items():
        ext = lib_stats.get(norm_key, {"total": 0, "passed": 0})
        acc_str = f"{(ext['passed'] / ext['total'] * 100.0):.1f}%" if ext['total'] > 0 else "N/A"

        total_tasks += info["tasks"]
        total_eval += ext["total"]
        total_v_passed += info["passed"]
        total_ext_passed += ext["passed"]

        rows.append(
            f"| **{info['name']}** | {info['tasks']} | {ext['total']} | {info['passed']} | "
            f"{info['accuracy']} | **{ext['passed']}** | **{acc_str}** |"
        )

    total_v_acc = f"{(total_v_passed / total_tasks * 100.0):.1f}%"
    total_ext_acc = f"{(total_ext_passed / total_eval * 100.0):.1f}%" if total_eval > 0 else "N/A"
    rows.append(
        f"| **Total** | **{total_tasks:,}** | **{total_eval}** | **{total_v_passed}** | "
        f"**{total_v_acc}** | **{total_ext_passed}** | **{total_ext_acc}** |"
    )

    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate benchmark comparison tables from runs/ directory")
    parser.add_argument("--runs-dir", default="runs", help="Path to runs/ folder")
    parser.add_argument("--update-md", action="store_true", help="Update benchmark_comparison.md in place")
    parser.add_argument("--output", default=None, help="Save generated markdown report to file")
    args = parser.parse_args()

    runs_path = Path(args.runs_dir).resolve()
    if not runs_path.exists():
        # Fallback check relative to script
        script_dir = Path(__file__).resolve().parent
        if (script_dir / "runs").exists():
            runs_path = script_dir / "runs"

    main_table = generate_main_table(runs_path)
    ds1000_table = generate_ds1000_library_table(runs_path)

    report = (
        "### 1. Results At A Glance (Head-to-Head Comparison)\n\n"
        f"{main_table}\n\n"
        "### 2. DS-1000 Breakdown By Library\n\n"
        f"{ds1000_table}\n"
    )

    print(report)

    if args.output:
        out_p = Path(args.output).resolve()
        out_p.write_text(report, encoding="utf-8")
        print(f"Table saved to: {out_p}")

    if args.update_md:
        md_file = Path("benchmark_comparison.md").resolve()
        if not md_file.exists():
            md_file = Path(__file__).resolve().parent / "benchmark_comparison.md"
        if md_file.exists():
            content = md_file.read_text(encoding="utf-8")
            # Replace Section 3 table
            s3_pattern = r"(## 3\. Results At A Glance.*?\n\n).*?(\n\n---|\n\n## 4)"
            new_s3 = f"## 3. Results At A Glance\n\nThe table below contrasts the Vanilla AgentCoder results against the live Extended AgentCoder 2.0 runs:\n\n{main_table}\n\n---"
            content = re.sub(s3_pattern, new_s3, content, flags=re.DOTALL)
            md_file.write_text(content, encoding="utf-8")
            print(f"Updated: {md_file}")


if __name__ == "__main__":
    main()
