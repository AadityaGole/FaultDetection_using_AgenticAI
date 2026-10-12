import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_GetToday-level-1-3_0", "level": 1, "dialogue_id": "GetToday-level-1-3", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"GetToday\\", \\"description\\": \\"This API gets the current date.\\", \\"input_parameters\\": {}, \\"output_parameters\\": {\\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The current date. Format: %Y-%m-%d\\"}}}", "dialogue_history": [], "expected_api_name": "GetToday", "expected_param_dict": {}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"GetToday\\", \\"description\\": \\"This API gets the current date.\\", \\"input_parameters\\": {}, \\"output_parameters\\": {\\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The current date. Format: %Y-%m-%d\\"}}}\\n\\nUser: Can you tell me the current date?\\nAI: Sure, I can do that.\\nGenerate API Request:"}'))
_generated_api_call = '[GetToday()]'

_expected_api_call = '[GetToday()]'
_wrong_api_call = '[DefinitelyNotGetToday()]'
_wrong_params_call = "[GetToday(unexpected_parameter='__unexpected__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
