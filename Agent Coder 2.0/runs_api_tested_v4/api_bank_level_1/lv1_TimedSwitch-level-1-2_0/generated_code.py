import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_TimedSwitch-level-1-2_0", "level": 1, "dialogue_id": "TimedSwitch-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"TimedSwitch\\", \\"description\\": \\"This API for setting a timed switch for a smart device.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the smart device.\\"}, \\"time\\": {\\"type\\": \\"str\\", \\"description\\": \\"The time to switch the device on or off. Format: %Y-%m-%d %H:%M:%S\\"}, \\"on\\": {\\"type\\": \\"bool\\", \\"description\\": \\"Whether to switch the device on or off.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the time switch is successful.\\"}}}", "dialogue_history": [], "expected_api_name": "TimedSwitch", "expected_param_dict": {"device_id": "1234", "time": "2021-12-05 19:00:00", "on": "True"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"TimedSwitch\\", \\"description\\": \\"This API for setting a timed switch for a smart device.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the smart device.\\"}, \\"time\\": {\\"type\\": \\"str\\", \\"description\\": \\"The time to switch the device on or off. Format: %Y-%m-%d %H:%M:%S\\"}, \\"on\\": {\\"type\\": \\"bool\\", \\"description\\": \\"Whether to switch the device on or off.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the time switch is successful.\\"}}}\\n\\nUser: Can you turn on my smart light at 7 PM tonight? Today is 2021-12-05.\\nAI: Sure, I can help with that. What is the ID of your smart light device?\\nUser: The ID is 1234.\\nAI: Got it. And just to confirm, you want me to turn on the smart light at 7 PM tonight, correct?\\nUser: That\'s right.\\nGenerate API Request:"}'))
_generated_api_call = "<|tool_call_start|>[ApiCall(api_name='TimedSwitch', arguments={'name': 'smart light', 'time': '2021-12-05 19:00:00', 'on': True})]<|tool_call_end|>"

_expected_api_call = "[TimedSwitch(device_id='1234', time='2021-12-05 19:00:00', on='True')]"
_wrong_api_call = "[DefinitelyNotTimedSwitch(device_id='1234', time='2021-12-05 19:00:00', on='True')]"
_wrong_params_call = "[TimedSwitch(device_id='__different_value_for_test__', time='2021-12-05 19:00:00', on='True')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
