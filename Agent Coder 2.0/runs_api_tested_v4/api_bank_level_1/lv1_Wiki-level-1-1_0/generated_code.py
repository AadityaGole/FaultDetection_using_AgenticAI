import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_Wiki-level-1-1_0", "level": 1, "dialogue_id": "Wiki-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Wiki\\", \\"description\\": \\"This API for searching a keyword in Wikipedia.\\", \\"input_parameters\\": {\\"keyword\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"dict\\", \\"description\\": \\"The list of results. Format be like {\\\\\\"url\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"summary\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"content\\\\\\": \\\\\\"xxx\\\\\\"}\\"}}}", "dialogue_history": [], "expected_api_name": "Wiki", "expected_param_dict": {"keyword": "artificial intelligence"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Wiki\\", \\"description\\": \\"This API for searching a keyword in Wikipedia.\\", \\"input_parameters\\": {\\"keyword\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"dict\\", \\"description\\": \\"The list of results. Format be like {\\\\\\"url\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"summary\\\\\\": \\\\\\"xxx\\\\\\", \\\\\\"content\\\\\\": \\\\\\"xxx\\\\\\"}\\"}}}\\n\\nUser: Can you help me search artificial intelligence on wikipedia?\\nAI: Sure.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='artificial intelligence')]"

_expected_api_call = "[Wiki(keyword='artificial intelligence')]"
_wrong_api_call = "[DefinitelyNotWiki(keyword='artificial intelligence')]"
_wrong_params_call = "[Wiki(keyword='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
