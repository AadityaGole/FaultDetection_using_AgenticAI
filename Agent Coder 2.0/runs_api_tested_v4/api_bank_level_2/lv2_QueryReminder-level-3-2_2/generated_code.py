import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv2_QueryReminder-level-3-2_2", "level": 2, "dialogue_id": "QueryReminder-level-3-2", "turn_id": 2, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}", "dialogue_history": [], "expected_api_name": "QueryReminder", "expected_param_dict": {"token": "o9i8u7y6t5r4e3w2q1", "content": "Book flight tickets", "time": "2023-03-22 08:00:00"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}\\n\\nUser: Can you help me set a reminder to book my flight tickets on March 22 at 8 AM?\\nAI: Sure, let me check first. [ToolSearcher(keywords=\'set reminder\')]\\nAPI-Request: [GetUserToken(username=\'user2\', password=\'user2pass\')]->{\'token\': \'o9i8u7y6t5r4e3w2q1\'}\\nGenerate API Request:"}'))
_generated_api_call = ''

_expected_api_call = "[QueryReminder(token='o9i8u7y6t5r4e3w2q1', content='Book flight tickets', time='2023-03-22 08:00:00')]"
_wrong_api_call = "[DefinitelyNotQueryReminder(token='o9i8u7y6t5r4e3w2q1', content='Book flight tickets', time='2023-03-22 08:00:00')]"
_wrong_params_call = "[QueryReminder(token='__different_value_for_test__', content='Book flight tickets', time='2023-03-22 08:00:00')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
