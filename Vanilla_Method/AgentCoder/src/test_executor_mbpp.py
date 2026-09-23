import random
import argparse
import json
from typing import Optional, Callable, Dict
import ast
import doctest
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import inspect
import numpy as np
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "CodeGeeX"))
import contextlib
import faulthandler
import io
import os
import multiprocessing
import platform
import signal
from tqdm import tqdm
from programmer_mbpp import call_completion
import tempfile
import subprocess
correct_before_doctest = 0
correct_after_doctest = 0
result_original = 0
result_canonical_solution = 0
result_fuzzer = 0
result_fuzzer_canonical_solution = 0
idx_run_tests_orginal = []
idx_run_tests_canonical_solution = []
idx_run_tests_fuzzer = []
idx_run_tests_fuzzer_canonical_solution = []

language = ["python","cpp","js","go","js"]


def process_humaneval_test(sample, problems, example_test=False,language=language, test_case=True,canonical_solution=False):
    task_id = sample["task_id"]
    task_id = problems.index(sample)
    prompt = sample["prompt"]
    code = sample["completion"]
    if canonical_solution:
        code = sample["code"]
    # Pre-process for different languages
    if language == "python" or language == "py":
        if test_case:
            tests = sample["test_case"]
        else:
            test_case = sample["test_list"]
            tests = ""
            for test in test_case:
                tests+="\n"+test
        test_string = code + "\n" + tests
    return test_string



def preprocess_data(task,lg):
    if f"```{lg}" in task["completion"]:
        task["completion"] = task["completion"][task["completion"].find(f"```{lg}") +len(f"```{lg}"):]
        task["completion"] = task["completion"][:task["completion"].find("```")]
    elif "```" in task["completion"]:
        task["completion"] = task["completion"][task["completion"].find("```") +3:]
        task["completion"] = task["completion"][:task["completion"].find("```")]

    if f"```{lg}" in task["prompt"]:
        task["prompt"] = task["prompt"][task["prompt"].find(f"```{lg}") +len(f"```{lg}"):]
        task["prompt"] = task["prompt"][:task["prompt"].find("```")]
    elif "```" in task["prompt"]:
        task["prompt"] = task["prompt"][task["prompt"].find("```") +3:]
        task["prompt"] = task["prompt"][:task["prompt"].find("```")]

    if "assert" in task["prompt"]:
        task["prompt"] = task["prompt"][:task["prompt"].find("assert")]
    return task


    




class TimeoutException(Exception):
    pass
class WriteOnlyStringIO(io.StringIO):
    """ StringIO that throws an exception when it's read from """

    def read(self, *args, **kwargs):
        raise IOError

    def readline(self, *args, **kwargs):
        raise IOError

    def readlines(self, *args, **kwargs):
        raise IOError

    def readable(self, *args, **kwargs):
        """ Returns True if the IO object can be read. """
        return False
class redirect_stdin(contextlib._RedirectStream):  # type: ignore
    _stream = 'stdin'

@contextlib.contextmanager
def swallow_io():
    stream = WriteOnlyStringIO()
    with contextlib.redirect_stdout(stream):
        with contextlib.redirect_stderr(stream):
            with redirect_stdin(stream):
                yield

@contextlib.contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

def run_stored_case(sample, lg):
    full_code = process_humaneval_test(sample, [sample], example_test=False, language=lg, test_case=False)
    tmp_dir = project_root / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", dir=tmp_dir, delete=False) as temp_file:
        temp_file.write(full_code)
        temp_path = temp_file.name
    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = (result.stdout + result.stderr).strip()
        return {"passed": result.returncode == 0, "result": output or "passed"}
    except subprocess.TimeoutExpired:
        return {"passed": False, "result": "timed out"}
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_report(dataset,lg):
    correct = 0
    for i in tqdm(range(len(dataset))):
        dataset[i]["full_code"] = process_humaneval_test(dataset[i], dataset, example_test=False,language=lg,test_case=False)
        result = run_stored_case(dataset[i], lg)
        if result["passed"]==True:
            correct+=1
        dataset[i]["report_passed"] = result["passed"]
        dataset[i]["report_result"] = result["result"]
    print("==============Start Report Testing==============")
    correct_percent = correct/len(dataset)*100
    print(f"test_report, {correct_percent:0.2f}")
    return dataset
    
def test_agent(dataset,lg):
    correct = 0
    for i in tqdm(range(len(dataset))):
        dataset[i]["full_code"] = process_humaneval_test(dataset[i], dataset, example_test=False,language=lg,test_case=False)
        result = run_stored_case(dataset[i], lg)
        if result["passed"]==True:
            correct+=1
        dataset[i]["result"] = result["result"]
        dataset[i]["passed"] = result["passed"]
    print("============Start Agent Testing=================")
    print("test_report",correct)
    return dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate stored MBPP cases with optional AgentCoder repair.")
    parser.add_argument("--offline", action="store_true", help="Only evaluate stored completions; do not call Kilo.")
    parser.add_argument("--epochs", type=int, default=1, help="Number of programmer repair rounds.")
    args = parser.parse_args()
    input_path = project_root / "dataset" / "zero_shot_gpt-3.5-turbo_4_mbpp.json"
    output_path = project_root / "dataset" / ("mbpp_existing_evaluation.json" if args.offline else "mbpp_agent_evaluation.json")
    with open(input_path, "r") as f:
        dataset = json.load(f)

    model = os.getenv("OPENAI_MODEL", "liquid/lfm-2.5-2.6b:free")
    if args.offline:
        evaluated_dataset = test_agent(dataset, "python")
    else:
        evaluated_dataset = dataset
        for epoch in range(args.epochs):
            print(f"AgentCoder generation round {epoch + 1}/{args.epochs} using {model}")
            evaluated_dataset = call_completion(evaluated_dataset, model, "py")
            generated_count = sum(item.get("agent_request_status") == "success" for item in evaluated_dataset)
            status_counts = {}
            for item in evaluated_dataset:
                status = item.get("agent_request_status", "skipped")
                status_counts[status] = status_counts.get(status, 0) + 1
            generated_path = project_root / "dataset" / f"mbpp_agent_round_{epoch + 1}_generated.json"
            with open(generated_path, "w") as f:
                json.dump(evaluated_dataset, f, indent=4)
            print(f"Fresh agent responses received: {generated_count}/{len(evaluated_dataset)}")
            print(f"Agent request statuses: {status_counts}")
            print(f"Saved generated output to {generated_path}")
            evaluated_dataset = test_agent(evaluated_dataset, "python")
    with open(output_path, "w") as f:
        json.dump(evaluated_dataset, f, indent=4)
    print(f"Saved existing-case evaluation to {output_path}")



