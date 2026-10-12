import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_DocumentQA-level-1-4_0", "level": 1, "dialogue_id": "DocumentQA-level-1-4", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"DocumentQA\\", \\"description\\": \\"This API answers the question from a given document url.\\", \\"input_parameters\\": {\\"url\\": {\\"type\\": \\"str\\", \\"description\\": \\"The url to download the document. It should end with .txt.\\"}, \\"question\\": {\\"type\\": \\"str\\", \\"description\\": \\"The question to be answered.\\"}}, \\"output_parameters\\": {\\"answer\\": {\\"type\\": \\"str\\", \\"description\\": \\"The answer to the question.\\"}}}", "dialogue_history": [], "expected_api_name": "DocumentQA", "expected_param_dict": {"url": "https://www.example.com/article-4.txt", "question": "What are the key features of this software?"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"DocumentQA\\", \\"description\\": \\"This API answers the question from a given document url.\\", \\"input_parameters\\": {\\"url\\": {\\"type\\": \\"str\\", \\"description\\": \\"The url to download the document. It should end with .txt.\\"}, \\"question\\": {\\"type\\": \\"str\\", \\"description\\": \\"The question to be answered.\\"}}, \\"output_parameters\\": {\\"answer\\": {\\"type\\": \\"str\\", \\"description\\": \\"The answer to the question.\\"}}}\\n\\nUser: Can you give me the key features of the software in this article - https://www.example.com/article-4.txt?\\nAI: Sure, what\'s the question you want me to answer?\\nUser: What are the key features of this software?\\nAI: Let me check.\\nGenerate API Request:"}'))
_generated_api_call = "[DocumentQA(url='https://www.example.com/article-4.txt', question='What are the key features of this software?')]"

_expected_api_call = "[DocumentQA(url='https://www.example.com/article-4.txt', question='What are the key features of this software?')]"
_wrong_api_call = "[DefinitelyNotDocumentQA(url='https://www.example.com/article-4.txt', question='What are the key features of this software?')]"
_wrong_params_call = "[DocumentQA(url='__different_value_for_test__', question='What are the key features of this software?')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
