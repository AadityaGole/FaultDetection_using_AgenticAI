import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv2_QueryStock-level-3-1_2", "level": 2, "dialogue_id": "QueryStock-level-3-1", "turn_id": 2, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}", "dialogue_history": [], "expected_api_name": "QueryStock", "expected_param_dict": {"stock_code": "MSFT", "date": "2022-02-04"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}\\n\\nUser: Can you please tell me the stock price of Microsoft on 4th February 2022?\\nAI: Sure, let me check.\\nAPI-Request: [ToolSearcher(keywords=\'Query Stock\')]->{\'name\': \'QueryStock\', \'description\': \'This API queries the stock price of a given stock.\', \'input_parameters\': {\'stock_code\': {\'type\': \'str\', \'description\': \'The stock code of the given stock.\'}, \'date\': {\'type\': \'str\', \'description\': \'The date of the stock price. Format: %Y-%m-%d\'}}, \'output_parameters\': {\'stock_price\': {\'type\': \'float\', \'description\': \'The stock price of the given stock.\'}}}\\nGenerate API Request:"}'))
_generated_api_call = "[QueryStock(key1='MSFT', key2='2022-02-04')]"

_expected_api_call = "[QueryStock(stock_code='MSFT', date='2022-02-04')]"
_wrong_api_call = "[DefinitelyNotQueryStock(stock_code='MSFT', date='2022-02-04')]"
_wrong_params_call = "[QueryStock(stock_code='__different_value_for_test__', date='2022-02-04')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
