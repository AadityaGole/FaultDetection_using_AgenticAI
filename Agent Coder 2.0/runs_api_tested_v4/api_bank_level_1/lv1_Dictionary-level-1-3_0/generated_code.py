import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_Dictionary-level-1-3_0", "level": 1, "dialogue_id": "Dictionary-level-1-3", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Dictionary\\", \\"description\\": \\"This API searches the dictionary for a given keyword.\\", \\"input_parameters\\": {\\"keyword\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results. Format be like [{\\\\\\"partOfSpeech\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"definitions\\\\\\": [{\\\\\\"definition\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"example\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"synonyms\\\\\\": [\\\\\\"xxx\\\\\\", \\\\\\"xxx\\\\\\"]}, ...]\\"}}}", "dialogue_history": [], "expected_api_name": "Dictionary", "expected_param_dict": {"keyword": "resilience"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Dictionary\\", \\"description\\": \\"This API searches the dictionary for a given keyword.\\", \\"input_parameters\\": {\\"keyword\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results. Format be like [{\\\\\\"partOfSpeech\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"definitions\\\\\\": [{\\\\\\"definition\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"example\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"synonyms\\\\\\": [\\\\\\"xxx\\\\\\", \\\\\\"xxx\\\\\\"]}, ...]\\"}}}\\n\\nUser: Can you give me the definition of the word \\"resilience\\"?\\nAI: Sure, let me check.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='resilience')]"

_expected_api_call = "[Dictionary(keyword='resilience')]"
_wrong_api_call = "[DefinitelyNotDictionary(keyword='resilience')]"
_wrong_params_call = "[Dictionary(keyword='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
