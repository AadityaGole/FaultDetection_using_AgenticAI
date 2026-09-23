import argparse
import ast
import json
import os
import re
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


def generate_api_call(history, api_names):
    prompt = (
        "Generate the next API request for this API-Bank dialogue. Return only one call "
        "in the exact format [ApiName(key='value')]. Do not explain.\n"
        f"Available API names: {', '.join(sorted(api_names))}\n\n"
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
        text = response.choices[0]["message"].get("content") or ""
        return text, "success", ""
    except Exception as exc:
        return "", "failed", repr(exc)


def main():
    parser = argparse.ArgumentParser(description="Run AgentCoder on API-Bank API-call turns.")
    parser.add_argument("--level", type=int, choices=[1, 2], default=1)
    parser.add_argument("--limit", type=int, default=0, help="Number of dialogue files; 0 means all.")
    args = parser.parse_args()
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
            generated, status, error = generate_api_call(history[:step], api_names)
            parsed = api_call_from_text(generated)
            expected = (item["api_name"], item["param_dict"])
            correct = parsed == expected
            results.append(
                {
                    "file": filename,
                    "step": step,
                    "expected_api": expected[0],
                    "expected_parameters": expected[1],
                    "generated": generated,
                    "parsed": parsed,
                    "agent_request_status": status,
                    "agent_error": error,
                    "passed": correct,
                }
            )

    output_path = PROJECT_ROOT / "dataset" / f"api_bank_level_{args.level}_agent_results.json"
    summary_path = PROJECT_ROOT / "dataset" / f"api_bank_level_{args.level}_agent_summary.json"
    summary = {
        "level": args.level,
        "count": len(results),
        "passed": sum(item["passed"] for item in results),
        "accuracy": sum(item["passed"] for item in results) / len(results) if results else 0,
        "request_status": dict(Counter(item["agent_request_status"] for item in results)),
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"Saved task results to {output_path}")
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
