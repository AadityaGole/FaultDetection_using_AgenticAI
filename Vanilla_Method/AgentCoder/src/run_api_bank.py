import argparse
import ast
import copy
import importlib
import inspect
import json
import os
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from pathlib import Path

import openai
import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
openai.api_key = os.getenv("OPENAI_API_KEY")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OPENAI_MODEL", "liquid/lfm-2.5-2.6b:free")
TIMEOUT = int(os.getenv("OPENAI_REQUEST_TIMEOUT", "15"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
GITHUB_RAW = "https://raw.githubusercontent.com/AlibabaResearch/DAMO-ConvAI/main/api-bank"
GITHUB_API = "https://api.github.com/repos/AlibabaResearch/DAMO-ConvAI/contents/api-bank"
API_BANK_REVISION = "188835d4f9948563a6b9c8ac50cd0f3ae4021ed6"
API_BANK_CACHE = Path.home() / ".cache" / "agentcoder" / "api-bank" / API_BANK_REVISION
NETWORK_BACKED_MOCKS = {"Dictionary", "Translate", "ToolSearcher"}


def list_sample_files(level):
    directory = "lv1-lv2-samples/level-1-given-desc" if level == 1 else "lv1-lv2-samples/level-2-toolsearcher"
    response = requests.get(f"{GITHUB_API}/{directory}", timeout=30)
    response.raise_for_status()
    return [(item["name"], f"{GITHUB_RAW}/{directory}/{item['name']}") for item in response.json() if item["name"].endswith(".jsonl")]


def load_dialogue(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return [json.loads(line) for line in response.text.splitlines() if line.strip()]


def api_call_from_text(text):
    match = re.search(r"\[([A-Za-z_]\w*)\((.*?)\)\]", text or "", re.DOTALL)
    if not match:
        return None
    expression = f"{match.group(1)}({match.group(2)})"
    try:
        call = ast.parse(expression, mode="eval").body
        if not isinstance(call, ast.Call):
            return None
        arguments = {keyword.arg: ast.literal_eval(keyword.value) for keyword in call.keywords}
        return call.func.id, arguments
    except (SyntaxError, ValueError, AttributeError):
        return None


def format_history(history):
    lines = []
    for item in history:
        role = item["role"]
        if role == "API":
            params = ", ".join(f"{key}={value!r}" for key, value in item["param_dict"].items())
            lines.append(f"API: [{item['api_name']}({params})] Response: {item['result']['output']!r}")
        else:
            lines.append(f"{role}: {item.get('text', '')}")
    return "\n".join(lines)


def generate_api_call(history, api_names, api_schemas=None):
    schema_text = json.dumps(api_schemas or {}, indent=2, ensure_ascii=False)
    prompt = (
        "Generate the next API request for this API-Bank dialogue. Return only one call "
        "in the exact format [ApiName(key='value')]. Use only parameters defined for that API. "
        "Do not explain.\n"
        f"Available API names: {', '.join(sorted(api_names))}\n\n"
        f"API descriptions and parameter schemas:\n{schema_text}\n\n"
        f"Conversation:\n{format_history(history)}"
    )
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            stream=False,
            max_tokens=MAX_TOKENS,
            request_timeout=TIMEOUT,
            messages=[
                {"role": "system", "content": "Return only the API call in square brackets."},
                {"role": "user", "content": prompt},
            ],
        )
        choice = response.choices[0]
        text = choice["message"].get("content") or ""
        if not text.strip():
            return "", "empty", "The model returned no message content"
        if choice.get("finish_reason") == "length":
            return text, "truncated", "The response reached the output token limit"
        return text, "success", ""
    except Exception as exc:
        return "", "failed", repr(exc)


def ensure_api_bank_sources():
    package_dir = API_BANK_CACHE / "apis"
    if (package_dir / "api.py").exists() and (API_BANK_CACHE / "init_database").is_dir():
        return

    tree_url = f"https://api.github.com/repos/AlibabaResearch/DAMO-ConvAI/git/trees/{API_BANK_REVISION}?recursive=1"
    response = requests.get(tree_url, timeout=60)
    response.raise_for_status()
    paths = [
        item["path"]
        for item in response.json()["tree"]
        if item["path"].startswith(("api-bank/apis/", "api-bank/init_database/"))
        and item["path"].endswith((".py", ".json"))
    ]

    def download(relative_path):
        path = API_BANK_CACHE / relative_path.removeprefix("api-bank/")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            url = f"https://raw.githubusercontent.com/AlibabaResearch/DAMO-ConvAI/{API_BANK_REVISION}/{relative_path}"
            result = requests.get(url, timeout=30)
            result.raise_for_status()
            path.write_bytes(result.content)

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(download, paths))
    (package_dir / "__init__.py").write_text("from .api import API\n", encoding="utf-8")


class ApiBankMockChecker:
    def __init__(self):
        ensure_api_bank_sources()
        sys.path.insert(0, str(API_BANK_CACHE))
        self.database_dir = API_BANK_CACHE / "init_database"
        self.databases = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in self.database_dir.glob("*.json")
        }
        self.class_modules = {}
        for path in (API_BANK_CACHE / "apis").glob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    self.class_modules[node.name] = path.stem
        importlib.invalidate_caches()

    def _load_class(self, api_name):
        module_name = self.class_modules.get(api_name)
        if not module_name:
            raise LookupError(f"API-Bank has no mock class for {api_name}")
        module = importlib.import_module(f"apis.{module_name}")
        return getattr(module, api_name)

    def describe(self, api_names):
        descriptions = {}
        for api_name in sorted(api_names):
            try:
                api_class = self._load_class(api_name)
                descriptions[api_name] = {
                    "description": getattr(api_class, "description", ""),
                    "parameters": getattr(api_class, "input_parameters", {}),
                }
            except Exception as exc:
                descriptions[api_name] = {"schema_unavailable": str(exc)}
        return descriptions

    def _make_instance(self, api_class, with_token_checker=True):
        constructor = inspect.signature(api_class.__init__).parameters
        kwargs = {}
        database_name = getattr(api_class, "database_name", None)
        if "init_database" in constructor:
            kwargs["init_database"] = copy.deepcopy(self.databases.get(database_name))
        if with_token_checker and "token_checker" in constructor:
            checker_class = self._load_class("CheckToken")
            kwargs["token_checker"] = self._make_instance(checker_class, with_token_checker=False)
        return api_class(**kwargs)

    @staticmethod
    def _convert_parameters(api_class, parameters):
        converted = {}
        schema = getattr(api_class, "input_parameters", {})
        for name, value in parameters.items():
            if name not in schema:
                raise ValueError(f"invalid parameter name: {name}")
            kind = schema[name]["type"]
            if kind == "int" and isinstance(value, str):
                value = int(value)
            elif kind == "float" and isinstance(value, str):
                value = float(value)
            elif kind == "bool" and isinstance(value, str):
                value = value == "True"
            elif kind in {"list", "list(str)"} and isinstance(value, str):
                value = ast.literal_eval(value)
            converted[name] = value
        return converted

    def check(self, api_name, parameters, ground_truth):
        if api_name in NETWORK_BACKED_MOCKS:
            return "skipped_external", False, f"{api_name} may access an external service"
        try:
            api_class = self._load_class(api_name)
            converted = self._convert_parameters(api_class, parameters)
            instance = self._make_instance(api_class)
        except (ValueError, TypeError, KeyError) as exc:
            return "invalid_call", False, str(exc)
        except ImportError as exc:
            return "unavailable_dependency", False, str(exc)
        except Exception as exc:
            return "failed", False, repr(exc)
        try:
            response = instance.call(**converted)
            passed = instance.check_api_call_correctness(response, ground_truth)
            return "success", bool(passed), json.dumps(response, default=str)
        except ImportError as exc:
            return "unavailable_dependency", False, str(exc)
        except Exception as exc:
            return "failed", False, repr(exc)


def main():
    parser = argparse.ArgumentParser(description="Run AgentCoder on API-Bank API-call turns.")
    parser.add_argument("--level", type=int, choices=[1, 2], default=1)
    parser.add_argument("--limit", type=int, default=0, help="Number of dialogue files; 0 means all.")
    parser.add_argument("--no-mock-check", action="store_true", help="Skip API-Bank local mock execution.")
    parser.add_argument("--reuse-generated", type=Path, help="Reuse generated calls from a prior results JSON; do not call the model.")
    args = parser.parse_args()
    mock_checker = None if args.no_mock_check else ApiBankMockChecker()
    cached_results = {}
    if args.reuse_generated:
        previous = json.loads(args.reuse_generated.read_text(encoding="utf-8"))
        cached_results = {(item["file"], item["step"]): item for item in previous}
    files = list_sample_files(args.level)
    if args.limit:
        files = files[: args.limit]
    results = []
    for filename, url in tqdm(files, desc=f"API-Bank level {args.level}"):
        history = load_dialogue(url)
        api_names = {item["api_name"] for item in history if item["role"] == "API"}
        for step, item in enumerate(history):
            if item["role"] != "API":
                continue
            cached = cached_results.get((filename, step))
            if args.reuse_generated:
                generated = cached.get("generated", "") if cached else ""
                status = cached.get("agent_request_status", "missing_cached_output") if cached else "missing_cached_output"
                error = cached.get("agent_error", "") if cached else "No saved result for this turn"
            else:
                schemas = mock_checker.describe(api_names) if mock_checker else None
                generated, status, error = generate_api_call(history[:step], api_names, schemas)
            parsed = api_call_from_text(generated)
            expected = (item["api_name"], item["param_dict"])
            correct = parsed == expected
            result = {
                "file": filename,
                "step": step,
                "expected_api": expected[0],
                "expected_parameters": expected[1],
                "expected_result": item["result"],
                "generated": generated,
                "parsed": parsed,
                "agent_request_status": status,
                "agent_error": error,
                "exact_match_passed": correct,
                "passed": correct,
            }
            if mock_checker and parsed:
                mock_status, mock_passed, mock_result = mock_checker.check(
                    parsed[0], parsed[1], item["result"]
                )
                result["mock_status"] = mock_status
                result["mock_passed"] = mock_passed
                result["mock_result"] = mock_result
            elif mock_checker:
                result["mock_status"] = "not_parseable"
                result["mock_passed"] = False
                result["mock_result"] = "Generated output did not parse as an API call"
            results.append(result)

    suffix = "_mock" if mock_checker else ""
    if args.reuse_generated:
        suffix += "_reused"
    output_path = PROJECT_ROOT / "dataset" / f"api_bank_level_{args.level}_agent_results{suffix}.json"
    summary_path = PROJECT_ROOT / "dataset" / f"api_bank_level_{args.level}_agent_summary{suffix}.json"
    summary = {
        "level": args.level,
        "count": len(results),
        "passed": sum(item["passed"] for item in results),
        "accuracy": sum(item["passed"] for item in results) / len(results) if results else 0,
        "request_status": dict(Counter(item["agent_request_status"] for item in results)),
    }
    if mock_checker:
        mock_checked = [item for item in results if item["mock_status"] == "success"]
        summary["mock_checked"] = len(mock_checked)
        summary["mock_passed"] = sum(item["mock_passed"] for item in mock_checked)
        summary["mock_accuracy"] = sum(item["mock_passed"] for item in mock_checked) / len(mock_checked) if mock_checked else 0
        summary["mock_status"] = dict(Counter(item["mock_status"] for item in results))
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"Saved task results to {output_path}")
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
