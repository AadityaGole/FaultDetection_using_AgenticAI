import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_EmergencyKnowledge-level-1-2_0", "level": 1, "dialogue_id": "EmergencyKnowledge-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"EmergencyKnowledge\\", \\"description\\": \\"This API searches for a given symptom for emergency knowledge.\\", \\"input_parameters\\": {\\"symptom\\": {\\"type\\": \\"str\\", \\"description\\": \\"The symptom to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results. Format be like [{\\\\\\"name\\\\\\":possible disease name, \\\\\\"aid\\\\\\": first-aid method},...]\\"}}}", "dialogue_history": [], "expected_api_name": "EmergencyKnowledge", "expected_param_dict": {"symptom": "headache"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"EmergencyKnowledge\\", \\"description\\": \\"This API searches for a given symptom for emergency knowledge.\\", \\"input_parameters\\": {\\"symptom\\": {\\"type\\": \\"str\\", \\"description\\": \\"The symptom to search.\\"}}, \\"output_parameters\\": {\\"results\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of results. Format be like [{\\\\\\"name\\\\\\":possible disease name, \\\\\\"aid\\\\\\": first-aid method},...]\\"}}}\\n\\nUser: Can you help me find information about my headache symptoms?\\nAI: Sure, I can search for information about your headache symptoms.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(symptom='headache')]"

_expected_api_call = "[EmergencyKnowledge(symptom='headache')]"
_wrong_api_call = "[DefinitelyNotEmergencyKnowledge(symptom='headache')]"
_wrong_params_call = "[EmergencyKnowledge(symptom='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
