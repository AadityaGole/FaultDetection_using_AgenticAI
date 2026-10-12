import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv2_QueryBalance-level-3-1_2", "level": 2, "dialogue_id": "QueryBalance-level-3-1", "turn_id": 2, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}", "dialogue_history": [], "expected_api_name": "QueryBalance", "expected_param_dict": {"token": "z9x8c7v6b5n4m3q2w1"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}\\n\\nUser: Hello, can you help me check my balance?\\nAI: Sure, can you please provide me with your username, password and email address?\\nUser: My username is foo, password is bar and email is foo@example.com.\\nAI: Thank you. Let me authenticate you first.\\nAPI-Request: [GetUserToken(username=\'foo\', password=\'bar\')]->{\'token\': \'z9x8c7v6b5n4m3q2w1\'}\\nAI: Okay, I have received your token. Now I will check your balance.\\nGenerate API Request:"}'))
_generated_api_call = ''

_expected_api_call = "[QueryBalance(token='z9x8c7v6b5n4m3q2w1')]"
_wrong_api_call = "[DefinitelyNotQueryBalance(token='z9x8c7v6b5n4m3q2w1')]"
_wrong_params_call = "[QueryBalance(token='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
