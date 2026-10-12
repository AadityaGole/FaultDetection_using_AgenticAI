import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_SymptomSearch-level-1-1_0", "level": 1, "dialogue_id": "SymptomSearch-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SymptomSearch\\", \\"description\\": \\"This API searches for a given symptom.\\", \\"input_parameters\\": {\\"symptom\\": {\\"type\\": \\"str\\", \\"description\\": \\"The symptom to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results. Format be like [{\\\\\\"name\\\\\\":possible disease name, \\\\\\"description\\\\\\": disease details},...]\\"}}}", "dialogue_history": [], "expected_api_name": "SymptomSearch", "expected_param_dict": {"symptom": "Abdominal pain"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SymptomSearch\\", \\"description\\": \\"This API searches for a given symptom.\\", \\"input_parameters\\": {\\"symptom\\": {\\"type\\": \\"str\\", \\"description\\": \\"The symptom to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results. Format be like [{\\\\\\"name\\\\\\":possible disease name, \\\\\\"description\\\\\\": disease details},...]\\"}}}\\n\\nUser: Can you help me find information on abdominal pain?\\nAI: Sure, I can help you with that. What specific information are you looking for?\\nUser: Just general information about abdominal pain and any potential causes or treatments.\\nAI: Okay, I understand. Let me use the SymptomSearch API to search for information on abdominal pain.\\nGenerate API Request:"}'))
_generated_api_call = "[SymptomSearch(symptom='abdominal pain')]"

_expected_api_call = "[SymptomSearch(symptom='Abdominal pain')]"
_wrong_api_call = "[DefinitelyNotSymptomSearch(symptom='Abdominal pain')]"
_wrong_params_call = "[SymptomSearch(symptom='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
