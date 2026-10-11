import argparse
import os
import json
from tqdm import tqdm
import copy
import openai
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Setting API parameters
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
openai.api_key = os.getenv("OPENAI_API_KEY")
project_root = Path(__file__).resolve().parents[1]
request_timeout = int(os.getenv("OPENAI_REQUEST_TIMEOUT", "15"))
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1024"))
worker_count = int(os.getenv("AGENT_WORKERS", "1"))

prompt_path = project_root / "prompts" / "mbpp_prompt_update.txt"
with open(prompt_path, "r") as f:
    construct_few_shot_prompt = f.read()

def preprocess_data(data,lg):
    if not data.get("completion"):
        data["completion"] = ""
    if f"```{lg}" in data["completion"]:
        data["completion"] = data["completion"][data["completion"].find(f"```{lg}")+len(f"```{lg}"):]
        data["completion"] = data["completion"][:data["completion"].find("```")]
    else:
        print(data["task_id"])
    return data

# Function to fetch completion
def fetch_completion(data_entry, model,lg):
    global construct_few_shot_prompt
    lg = "py"
    prompt = data_entry["prompt"]
    test_case = data_entry["test_list"]
    tests = ""
    for test in test_case:
        tests+="\n"+test
    text = f"""Complete the Python function below. Return only the completed code, with no reasoning or explanation.

Task:
{prompt}

The code must pass these tests:
{tests}
"""
    try:
        completions = openai.ChatCompletion.create(
            model = model,
            stream=False,
            messages=[
                {"role": "system", "content": "Return only working Python code. Do not show reasoning."},
        {"role": "user", "content":text},
            ],
            max_tokens=max_tokens,
            request_timeout=request_timeout,
        )
        generated_completion = completions.choices[0]["message"].get("content") or ""
        data_entry["agent_generated_completion"] = generated_completion
        data_entry["agent_request_status"] = "success" if generated_completion else "empty"
        if generated_completion:
            data_entry["completion"] = generated_completion
        data_entry = preprocess_data(data_entry,lg)
        return data_entry
    except Exception as e:
        data_entry["agent_generated_completion"] = ""
        data_entry["agent_request_status"] = "failed"
        data_entry["agent_error"] = repr(e)
        print(f"Agent request failed for task {data_entry.get('task_id')}: {e}")
        data_entry["completion"] = data_entry.get("completion", "")
        return data_entry

def fix_bug(data_entry, model,lg,preprocess_data = preprocess_data):
    if "passed" in data_entry.keys() and data_entry["passed"] == True:
        return data_entry
    else:
        gpt_prompt = (
            "Please re-completion the code to fix the error message. "+
            f"\nHere is the previous version:\n```{lg}\n" + 
            data_entry['completion'] + f"\n```\nWhen we use this test cases: ```{lg}\n"+data_entry["test_case"]+f"\n``` to evaluate the code. It raise the error:\n```{lg}\n" + data_entry["result"] +
            f"\n```\nPlease fix the bug and return the code. The re-completion code should in triple backticks format(i.e., in ```{lg} ```)."
        )
        try:
            completions = openai.ChatCompletion.create(
                model = model,
                stream=False,
                messages=[
            {"role": "system", "content": "You are a code developer assistant."},
            {"role": "user", "content":gpt_prompt},
                ],
                request_timeout=100,
            )
            data_entry["completion"] = completions.choices[0]["message"]["content"]
            data_entry = preprocess_data(data_entry,"py")
        except Exception as e:
            print(repr(e))
    return data_entry

def call_fix_bug(dataset, model,lg):
    print("Fixing bug...")
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model, lg): entry for entry in tqdm(dataset)}
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))
    return dataset

def call_completion(dataset, model,lg):
    print("Fixing bug...")
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model, lg): entry for entry in tqdm(dataset)}
        for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
            entry = future_to_entry[future]
            try:
                updated_entry = future.result()
                idx = dataset.index(entry)
                dataset[idx] = updated_entry
            except Exception as e:
                print(repr(e))
    return dataset



if __name__ == "__main__":
    model_list = [os.getenv("OPENAI_MODEL", "liquid/lfm-2.5-2.6b:free")]
    language = ["py"]
    for model in model_list:
        for lg in language:
            from datasets import load_dataset
            dataset = load_dataset("mbpp",name="sanitized",split="test")
            dataset = [entry for entry in dataset]
            with open(path, "r") as f:
                dataset = json.load(f)
            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_entry = {executor.submit(fetch_completion, copy.deepcopy(entry), model, lg): entry for entry in tqdm(dataset)}
                for future in tqdm(concurrent.futures.as_completed(future_to_entry)):
                    entry = future_to_entry[future]
                    try:
                        updated_entry = future.result()
                        idx = dataset.index(entry)
                        dataset[idx] = updated_entry
                    except Exception as e:
                        print(repr(e))

            with open(f"./dataset/{model}_mbpp.json", "w") as f:
                json.dump(dataset, f, indent=4)
