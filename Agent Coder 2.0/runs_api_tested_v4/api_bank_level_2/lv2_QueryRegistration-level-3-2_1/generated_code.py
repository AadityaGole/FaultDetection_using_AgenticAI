import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv2_QueryRegistration-level-3-2_1", "level": 2, "dialogue_id": "QueryRegistration-level-3-2", "turn_id": 1, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}", "dialogue_history": [], "expected_api_name": "QueryRegistration", "expected_param_dict": {"patient_name": "John Doe", "date": "2023-04-12"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ToolSearcher\\", \\"description\\": \\"Searches for relevant tools in library based on the keywords.\\", \\"input_parameters\\": {\\"keywords\\": {\\"type\\": \\"str\\", \\"description\\": \\"The keyword to search for.\\"}}, \\"output_parameters\\": {\\"best_matchs\\": {\\"type\\": \\"Union[List[dict], dict]\\", \\"description\\": \\"The best match tool(s).\\"}}}\\n\\nUser: Can you please check if I have an appointment on April 12th?\\nAI: Sure, may I know your name please?\\nUser: John Doe\\nAPI-Request: [ToolSearcher(keywords=\'Query Registration\')]->{\'name\': \'QueryRegistration\', \'description\': \'This API queries the registration of a patient given patient ID.\', \'input_parameters\': {\'patient_name\': {\'type\': \'str\', \'description\': \'The name of patient.\'}, \'date\': {\'type\': \'str\', \'description\': \'The date of appointment. Format be like %Y-%m-%d\'}}, \'output_parameters\': {\'appointments\': {\'type\': \'list\', \'description\': \'The dict where from appointment_id to a list like [\\"patient_name\\":xxx, \\"date\\":xxx, \\"doctor_name\\":xxx]\'}}}\\nGenerate API Request:"}'))
_generated_api_call = ''

_expected_api_call = "[QueryRegistration(patient_name='John Doe', date='2023-04-12')]"
_wrong_api_call = "[DefinitelyNotQueryRegistration(patient_name='John Doe', date='2023-04-12')]"
_wrong_params_call = "[QueryRegistration(patient_name='__different_value_for_test__', date='2023-04-12')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
