import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_QueryStock-level-1-1_0", "level": 1, "dialogue_id": "QueryStock-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryStock\\", \\"description\\": \\"This API queries the stock price of a given stock code and date.\\", \\"input_parameters\\": {\\"stock_code\\": {\\"type\\": \\"str\\", \\"description\\": \\"The stock code of the given stock.\\"}, \\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The date of the stock price. Format: %Y-%m-%d\\"}}, \\"output_parameters\\": {\\"stock_price\\": {\\"type\\": \\"float\\", \\"description\\": \\"The stock price of the given stock.\\"}}}", "dialogue_history": [], "expected_api_name": "QueryStock", "expected_param_dict": {"stock_code": "SQ", "date": "2022-03-14"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryStock\\", \\"description\\": \\"This API queries the stock price of a given stock code and date.\\", \\"input_parameters\\": {\\"stock_code\\": {\\"type\\": \\"str\\", \\"description\\": \\"The stock code of the given stock.\\"}, \\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The date of the stock price. Format: %Y-%m-%d\\"}}, \\"output_parameters\\": {\\"stock_price\\": {\\"type\\": \\"float\\", \\"description\\": \\"The stock price of the given stock.\\"}}}\\n\\nUser: What is the stock price of SQ on March 14th, 2022?\\nAI: Let me check for you.\\nGenerate API Request:"}'))
_generated_api_call = "API-Request: [QueryStock(stock_code='SQ', date='2022-03-14')]"

_expected_api_call = "[QueryStock(stock_code='SQ', date='2022-03-14')]"
_wrong_api_call = "[DefinitelyNotQueryStock(stock_code='SQ', date='2022-03-14')]"
_wrong_params_call = "[QueryStock(stock_code='__different_value_for_test__', date='2022-03-14')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
