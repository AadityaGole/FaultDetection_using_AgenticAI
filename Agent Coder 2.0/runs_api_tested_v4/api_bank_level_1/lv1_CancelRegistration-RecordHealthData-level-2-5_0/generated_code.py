import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_CancelRegistration-RecordHealthData-level-2-5_0", "level": 1, "dialogue_id": "CancelRegistration-RecordHealthData-level-2-5", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"CancelRegistration\\", \\"description\\": \\"This API cancels the registration of a patient given appointment ID.\\", \\"input_parameters\\": {\\"appointment_id\\": {\\"type\\": \\"str\\", \\"description\\": \\"The ID of appointment.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The status of cancellation.\\"}}}", "dialogue_history": [], "expected_api_name": "CancelRegistration", "expected_param_dict": {"appointment_id": "56789012"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"CancelRegistration\\", \\"description\\": \\"This API cancels the registration of a patient given appointment ID.\\", \\"input_parameters\\": {\\"appointment_id\\": {\\"type\\": \\"str\\", \\"description\\": \\"The ID of appointment.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The status of cancellation.\\"}}}\\n\\nUser: Can you please cancel my appointment for David Brown with Dr. Davis on April 10th, 2023 at 10:00 am?\\nAI: Sure, I can help you with that. What\'s your appointment ID?\\nUser: 56789012\\nAI: I\'m cancelling your appointment with ID 56789012.\\nGenerate API Request:"}'))
_generated_api_call = "[CancelRegistration(appointment_id='56789012')]"

_expected_api_call = "[CancelRegistration(appointment_id='56789012')]"
_wrong_api_call = "[DefinitelyNotCancelRegistration(appointment_id='56789012')]"
_wrong_params_call = "[CancelRegistration(appointment_id='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
