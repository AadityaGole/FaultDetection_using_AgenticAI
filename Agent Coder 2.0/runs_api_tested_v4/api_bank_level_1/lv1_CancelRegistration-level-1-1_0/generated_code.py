import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_CancelRegistration-level-1-1_0", "level": 1, "dialogue_id": "CancelRegistration-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"CancelRegistration\\", \\"description\\": \\"This API cancels the registration of a patient given appointment ID.\\", \\"input_parameters\\": {\\"appointment_id\\": {\\"type\\": \\"str\\", \\"description\\": \\"The ID of appointment.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The status of cancellation.\\"}}}", "dialogue_history": [], "expected_api_name": "CancelRegistration", "expected_param_dict": {"appointment_id": "90123456"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"CancelRegistration\\", \\"description\\": \\"This API cancels the registration of a patient given appointment ID.\\", \\"input_parameters\\": {\\"appointment_id\\": {\\"type\\": \\"str\\", \\"description\\": \\"The ID of appointment.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The status of cancellation.\\"}}}\\n\\nUser: Can you cancel my registration for appointment ID 90123456?\\nAI: Sure, may I have the patient name, appointment date, and doctor\'s name for verification?\\nUser: Olivia Davis, October 10th, Dr. Smith.\\nGenerate API Request:"}'))
_generated_api_call = "<|tool_call_start|>[ApiCall(api_name='CancelRegistration', arguments={'appointment_id': '90123456'})]<|tool_call_end|>"

_expected_api_call = "[CancelRegistration(appointment_id='90123456')]"
_wrong_api_call = "[DefinitelyNotCancelRegistration(appointment_id='90123456')]"
_wrong_params_call = "[CancelRegistration(appointment_id='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
