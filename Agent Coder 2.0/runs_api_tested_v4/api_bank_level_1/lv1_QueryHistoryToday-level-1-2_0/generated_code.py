import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_QueryHistoryToday-level-1-2_0", "level": 1, "dialogue_id": "QueryHistoryToday-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryHistoryToday\\", \\"description\\": \\"This API queries the history of the given date.\\", \\"input_parameters\\": {\\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The date of the history. Format: %m-%d\\"}}, \\"output_parameters\\": {\\"history\\": {\\"type\\": \\"list\\", \\"description\\": \\"The history of the user today.\\"}}}", "dialogue_history": [], "expected_api_name": "QueryHistoryToday", "expected_param_dict": {"date": "12-10"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryHistoryToday\\", \\"description\\": \\"This API queries the history of the given date.\\", \\"input_parameters\\": {\\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The date of the history. Format: %m-%d\\"}}, \\"output_parameters\\": {\\"history\\": {\\"type\\": \\"list\\", \\"description\\": \\"The history of the user today.\\"}}}\\n\\nUser: Can you tell me what happened on this day in history?\\nAI: Sure, what specific day are you interested in?\\nUser: Today\'s date, December 10th.\\nAI: Ok, let me check.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='date', key2='12-10')]"

_expected_api_call = "[QueryHistoryToday(date='12-10')]"
_wrong_api_call = "[DefinitelyNotQueryHistoryToday(date='12-10')]"
_wrong_params_call = "[QueryHistoryToday(date='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
