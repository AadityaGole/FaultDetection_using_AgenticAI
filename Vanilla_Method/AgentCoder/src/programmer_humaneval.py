import argparse
import os
import json
from tqdm import tqdm
import copy
import openai
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
from pathlib import Path
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

# Setting API parameters
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
openai.api_key = os.getenv("OPENAI_API_KEY")
project_root = Path(__file__).resolve().parents[1]
completion_count = int(os.getenv("COMPLETIONS_PER_TASK", "1"))
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
request_timeout = int(os.getenv("OPENAI_REQUEST_TIMEOUT", "30"))
max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
worker_count = int(os.getenv("AGENT_WORKERS", "5"))

dataset = load_dataset("openai/openai_humaneval",split="test")
dataset = [entry for entry in dataset]

prompt_path = project_root / "prompts" / "humaneval_prompt_update.txt"
with open(prompt_path, "r") as f:
    construct_few_shot_prompt = f.read()

def preprocess_data(completion_string):
    if not completion_string:
        return ""
    if f"```python" in completion_string:
        completion_string = completion_string[completion_string.find(f"```python")+len(f"```python"):]
        closing_fence = completion_string.find("```")
        if closing_fence != -1:
            completion_string = completion_string[:closing_fence]
    return completion_string

# Function to fetch completion
def fetch_completion(data_entry, model,lg,times=completion_count):
    global construct_few_shot_prompt
    if "need_reproduce" in data_entry.keys() and data_entry["need_reproduce"]==False:
        return data_entry
    prompt = data_entry["prompt"]
    text = f"""Complete this Python function. Return only the missing code, with no explanation or Markdown fences.

```python
{prompt}
```"""
    completions_code = []
    for i in range(times):
        completion = ""
        for attempt in range(max_retries + 1):
            try:
                completions = openai.ChatCompletion.create(
                    model=model,
                        max_tokens=max_tokens,
                    stream=False,
                    messages=[
                {"role": "system", "content": "Return only the completed Python code. Do not show reasoning."},
                {"role": "user", "content":text},
                    ],
                    request_timeout=request_timeout,
                )
                completion = completions.choices[0]["message"]["content"]
                completion = preprocess_data(completion)

            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if "invalid" in str(e).lower() and "token" in str(e).lower():
                    raise RuntimeError(
                        "API authentication failed. Check OPENAI_API_KEY and "
                        "OPENAI_BASE_URL in .env."
                    ) from e
                if attempt < max_retries:
                    time.sleep(2)
            if completion != "":
                break
        if completion == "":
            print("Skipping task after repeated request failures.")
        completions_code.append(completion)
    data_entry["completion_list"] = completions_code
    return data_entry


def call_fetch_completion_helper(dataset, model,lg):
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
    language = ["python"]
    for model in model_list:
        for lg in language:
            from datasets import load_dataset
            dataset = load_dataset("openai/openai_humaneval",split="test")
            dataset = [entry for entry in dataset]
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
            output_path = project_root / "dataset" / f"{model.replace('/', '_')}_{lg}.json"
            with open(output_path, "w") as f:
                json.dump(dataset, f, indent=4)
