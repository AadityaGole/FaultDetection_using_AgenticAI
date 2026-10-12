import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_SearchEngine-level-1-2_0", "level": 1, "dialogue_id": "SearchEngine-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SearchEngine\\", \\"description\\": \\"This API searches for a given keyword for search engine.\\", \\"input_parameters\\": {\\"keyword\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results.\\"}}}", "dialogue_history": [], "expected_api_name": "SearchEngine", "expected_param_dict": {"keyword": "the sustainable development"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SearchEngine\\", \\"description\\": \\"This API searches for a given keyword for search engine.\\", \\"input_parameters\\": {\\"keyword\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results.\\"}}}\\n\\nUser: Can you search for news articles about sustainable development goals?\\nAI: Sure, what specific keyword are you looking for?\\nUser: the sustainable development?\\nAI: OK.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='sustainable development')]"

_expected_api_call = "[SearchEngine(keyword='the sustainable development')]"
_wrong_api_call = "[DefinitelyNotSearchEngine(keyword='the sustainable development')]"
_wrong_params_call = "[SearchEngine(keyword='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
