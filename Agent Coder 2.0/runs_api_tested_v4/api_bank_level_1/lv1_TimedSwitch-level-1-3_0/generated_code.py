import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_TimedSwitch-level-1-3_0", "level": 1, "dialogue_id": "TimedSwitch-level-1-3", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"TimedSwitch\\", \\"description\\": \\"This API for setting a timed switch for a smart device.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the smart device.\\"}, \\"time\\": {\\"type\\": \\"str\\", \\"description\\": \\"The time to switch the device on or off. Format: %Y-%m-%d %H:%M:%S\\"}, \\"on\\": {\\"type\\": \\"bool\\", \\"description\\": \\"Whether to switch the device on or off.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the time switch is successful.\\"}}}", "dialogue_history": [], "expected_api_name": "TimedSwitch", "expected_param_dict": {"device_id": "123456", "time": "2022-03-01 22:00:00", "on": "False"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"TimedSwitch\\", \\"description\\": \\"This API for setting a timed switch for a smart device.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the smart device.\\"}, \\"time\\": {\\"type\\": \\"str\\", \\"description\\": \\"The time to switch the device on or off. Format: %Y-%m-%d %H:%M:%S\\"}, \\"on\\": {\\"type\\": \\"bool\\", \\"description\\": \\"Whether to switch the device on or off.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the time switch is successful.\\"}}}\\n\\nUser: Can you switch off my smart bulb at 10 pm tonight? Today is 2022-03-01.\\nAI: Sure, I can do that for you. What\'s the device ID of your smart bulb?\\nUser: It\'s 123456.\\nAI: Got it. And what time do you want me to switch it off?\\nUser: 10 pm tonight.\\nAI: Understood. Switching off your smart bulb at 10 pm tonight. Please wait a moment.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(name='smart bulb', time='2022-03-01 22:00:00', on=True)]"

_expected_api_call = "[TimedSwitch(device_id='123456', time='2022-03-01 22:00:00', on='False')]"
_wrong_api_call = "[DefinitelyNotTimedSwitch(device_id='123456', time='2022-03-01 22:00:00', on='False')]"
_wrong_params_call = "[TimedSwitch(device_id='__different_value_for_test__', time='2022-03-01 22:00:00', on='False')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
