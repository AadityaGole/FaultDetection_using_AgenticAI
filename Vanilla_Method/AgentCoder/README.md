# AgentCoder: multi-agent code generation framework

AgentCoder is a novel multiagent-code generation framework that leverages the power of large language models (LLMs) to enhance the effectiveness of code generation. The framework consists of three specialized agents: the programmer agent, the test designer agent, and the test executor agent. These agents collaborate to generate high-quality code snippets, design comprehensive test cases, and ensure the correctness of the generated code through an iterative feedback loop.

## Key Features

- **Multiagent Collaboration**: AgentCoder utilizes a multiagent framework where each agent specializes in a specific task, leading to improved code generation effectiveness.
- **Independent Test Case Generation**: The test designer agent generates diverse and objective test cases independently, ensuring comprehensive testing of the generated code.
- **Iterative Code Refinement**: The test executor agent executes the generated test cases against the code and provides feedback to the programmer agent for iterative code refinement.
- **Modularity and Scalability**: The modular structure of AgentCoder allows for easy integration with advanced models and future enhancements, ensuring adaptability in the evolving landscape of code generation.

## Installation

To use AgentCoder, you need to have an API key from OpenAI or other similar third-party providers.
1. Clone the AgentCoder repository:
   ```
   git clone https://github.com/your-username/AgentCoder.git
   cd AgentCoder
   git clone https://github.com/THUDM/CodeGeeX
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Add your API key in the `.env` file:
   ```python
   OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
   ```

## Usage

### Code Generation

To generate code snippets, run the following commands:
```
python programmer_[humaneval/mbpp].py
```
These scripts will generate code snippets that will be used for test case generation.

### Test Case Generation

To generate test cases, run the following command:
```
python test_designer_[humaneval/mbpp].py
```
This script will generate diverse and comprehensive test cases based on the coding requirements.

### Self-Optimization Process

To perform the self-optimization process, run the following commands:
```
python test_executor_[humaneval/mbpp].py
```

### DS-1000 and API-Bank

Run AgentCoder on the official DS-1000 data. This generates a fresh solution for
each task, executes the official `code_context` tests, and saves per-task results
and a library summary under `dataset/`:

```
python src/run_ds1000.py
```

Use `--limit 10` for a small run while checking the API configuration.

Run AgentCoder on API-Bank level-1 API-call turns:

```
python src/run_api_bank.py --level 1
```

Use `--level 2` for the tool-searcher conversations. Both runners save raw
generated output, request status, parsed output, pass/fail results, and summary
JSON files in `dataset/`.
These scripts will execute the generated test cases against the code and provide feedback to the programmer agent for iterative code refinement.

Run AgentCoder on BigCodeBench Instruct with a small smoke test:

```
python .\run_bigcodebench.py --limit 5
```

Run all 1,140 tasks with:

```
python .\run_bigcodebench.py
```

BigCodeBench solutions are evaluated by its official hosted evaluator. Generated
samples, per-task results, the summary, and raw evaluator output are saved under
`dataset/`. Re-evaluate saved generations without calling the model using:

```
python .\run_bigcodebench.py --reuse-samples ..\dataset\bigcodebench_instruct_agent_samples.jsonl
```

Install the hosted evaluator client with `pip install -r requirements.txt`.

Latest full BigCodeBench Instruct result: `125/1,140` passed (`pass@1 = 11.0%`).
Request statuses were 206 successful, 775 empty, 99 truncated, and 60 failed.
The official evaluator's ground-truth pass rate was 99.65% (1,136/1,140), which
validates the benchmark tests rather than measuring model accuracy. Per-task
results include official evaluator status and failure details.

Latest API-Bank run results (389 level-1 turns and 119 level-2 turns):

| Split | Exact-match accuracy | Local mock accuracy | Mock coverage |
|---|---:|---:|---:|
| Level 1 | 55.5% (216/389) | 80.8% (232/287 checked) | 73.8% (287/389) |
| Level 2 | 28.6% (34/119) | 73.1% (38/52 checked) | 43.7% (52/119) |

Mock accuracy is conditional on a call being parseable and supported by an
available local mock. Empty, truncated, invalid, externally-backed, and
dependency-unavailable calls are reported separately. See
`benchmark_comparison.md` for request-status counts and full benchmark context.


## Contributions

Contributions to AgentCoder are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

AgentCoder is released under the [MIT License](LICENSE).

## Acknowledgments

We would like to thank AIOHUB for providing funding and support for the development of AgentCoder. We also acknowledge the contributions of the open-source community and the developers of the large language models used in this project.
