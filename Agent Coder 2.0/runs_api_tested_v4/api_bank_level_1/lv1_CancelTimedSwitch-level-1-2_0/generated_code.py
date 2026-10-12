import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_CancelTimedSwitch-level-1-2_0", "level": 1, "dialogue_id": "CancelTimedSwitch-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"CancelTimedSwitch\\", \\"description\\": \\"Cancels a timed switch for a smart device.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the smart device.\\"}, \\"time\\": {\\"type\\": \\"str\\", \\"description\\": \\"The time to switch the device on or off. Format: %Y-%m-%d %H:%M:%S\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the time switch is successful.\\"}}}", "dialogue_history": [], "expected_api_name": "CancelTimedSwitch", "expected_param_dict": {"device_id": "10000025", "time": "2023-03-19 09:30:00"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"CancelTimedSwitch\\", \\"description\\": \\"Cancels a timed switch for a smart device.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the smart device.\\"}, \\"time\\": {\\"type\\": \\"str\\", \\"description\\": \\"The time to switch the device on or off. Format: %Y-%m-%d %H:%M:%S\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the time switch is successful.\\"}}}\\n\\nUser: Can you cancel a timed switch for my smart device?\\nAI: Sure, I can help with that. Please provide me the ID of your smart device.\\nUser: It\'s 10000025.\\nAI: And what\'s the time for the current timed switch?\\nUser: It\'s set for March 19th, 2023 at 9:30 AM.\\nAI: Understood. Let me just call the CancelTimedSwitch API to cancel the timed switch.\\nGenerate API Request:"}'))
_generated_api_call = "<|tool_call_start|>[ApiCall(api_name='CancelTimedSwitch', arguments={'name': '10000025', 'time': '2023-03-19 09:30:00'})]<|tool_call_end|>"

_expected_api_call = "[CancelTimedSwitch(device_id='10000025', time='2023-03-19 09:30:00')]"
_wrong_api_call = "[DefinitelyNotCancelTimedSwitch(device_id='10000025', time='2023-03-19 09:30:00')]"
_wrong_params_call = "[CancelTimedSwitch(device_id='__different_value_for_test__', time='2023-03-19 09:30:00')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
