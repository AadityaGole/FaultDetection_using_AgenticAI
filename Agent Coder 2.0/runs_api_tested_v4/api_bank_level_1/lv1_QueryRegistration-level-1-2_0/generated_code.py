import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_QueryRegistration-level-1-2_0", "level": 1, "dialogue_id": "QueryRegistration-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryRegistration\\", \\"description\\": \\"This API queries the registration of a patient, given patient ID.\\", \\"input_parameters\\": {\\"patient_name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of patient.\\"}, \\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The date of appointment. Format be like %Y-%m-%d\\"}}, \\"output_parameters\\": {\\"appointments\\": {\\"type\\": \\"list\\", \\"description\\": \\"The dict where from appointment_id to a list like [\\\\\\"patient_name\\\\\\":xxx, \\\\\\"date\\\\\\":xxx, \\\\\\"doctor_name\\\\\\":xxx]\\"}}}", "dialogue_history": [], "expected_api_name": "QueryRegistration", "expected_param_dict": {"patient_name": "Olivia Davis", "date": "2023-10-10"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryRegistration\\", \\"description\\": \\"This API queries the registration of a patient, given patient ID.\\", \\"input_parameters\\": {\\"patient_name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of patient.\\"}, \\"date\\": {\\"type\\": \\"str\\", \\"description\\": \\"The date of appointment. Format be like %Y-%m-%d\\"}}, \\"output_parameters\\": {\\"appointments\\": {\\"type\\": \\"list\\", \\"description\\": \\"The dict where from appointment_id to a list like [\\\\\\"patient_name\\\\\\":xxx, \\\\\\"date\\\\\\":xxx, \\\\\\"doctor_name\\\\\\":xxx]\\"}}}\\n\\nUser: Can you help me find out my next appointment with Dr. Smith on October 10th, 2023? My patient ID is 90123456 and my name is Olivia Davis.\\nAI: Sure, let me check that for you.\\nGenerate API Request:"}'))
_generated_api_call = "<|tool_call_start|>[ApiCall(api_name='QueryRegistration', parameters={'patient_name': 'Olivia Davis', 'date': '2023-10-10'})]<|tool_call_end|>"

_expected_api_call = "[QueryRegistration(patient_name='Olivia Davis', date='2023-10-10')]"
_wrong_api_call = "[DefinitelyNotQueryRegistration(patient_name='Olivia Davis', date='2023-10-10')]"
_wrong_params_call = "[QueryRegistration(patient_name='__different_value_for_test__', date='2023-10-10')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
