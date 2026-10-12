import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv2_SymptomSearch-level-3-4_1", "level": 2, "dialogue_id": "SymptomSearch-level-3-4", "turn_id": 1, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}", "dialogue_history": [], "expected_api_name": "SymptomSearch", "expected_param_dict": {"symptom": "rash"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}\\n\\nUser: Can you help me find some information on a rash I\'ve been experiencing?\\nAI: Sure.\\nAPI-Request: [ToolSearcher(keywords=\'rash\')]->{\'name\': \'SymptomSearch\', \'description\': \'This API searches for a given symptom.\', \'input_parameters\': {\'symptom\': {\'type\': \'str\', \'description\': \'The symptom to search.\'}}, \'output_parameters\': {\'results\': {\'type\': \'list\', \'description\': \'The list of results. Format be like [{\\"name\\":possible disease name, \\"description\\": disease details},...]\'}}}\\nGenerate API Request:"}'))
_generated_api_call = "[ToolSearcher(keywords='rash')]"

_expected_api_call = "[SymptomSearch(symptom='rash')]"
_wrong_api_call = "[DefinitelyNotSymptomSearch(symptom='rash')]"
_wrong_params_call = "[SymptomSearch(symptom='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
