import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv2_QueryReminder-level-3-1_0", "level": 2, "dialogue_id": "QueryReminder-level-3-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}", "dialogue_history": [], "expected_api_name": "GetUserToken", "expected_param_dict": {"username": "user2", "password": "user2pass"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}\\n\\nUser: Can you help me set a reminder to book flight tickets for March 22 at 8 am?\\nAI: Sure! Let me just search for the relevant tool. [ToolSearcher(keywords=\'reminder ticket booking\')] Based on my search, I can use the QueryReminder API for this. Do you have a token to use for authentication?\\nUser: No, I don\'t have a token.\\nAI: Not a problem. I\'ll just get a token for you using the GetUserToken API. Can you please give me your username and password?\\nUser: My username is user2 and my password is user2pass.\\nGenerate API Request:"}'))
_generated_api_call = "<|tool_call_start|>[ToolSearcher(keywords='reminder ticket booking'), GetUserToken(username='user2', password='user2pass')]<|tool_call_end|>"

_expected_api_call = "[GetUserToken(username='user2', password='user2pass')]"
_wrong_api_call = "[DefinitelyNotGetUserToken(username='user2', password='user2pass')]"
_wrong_params_call = "[GetUserToken(username='__different_value_for_test__', password='user2pass')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
