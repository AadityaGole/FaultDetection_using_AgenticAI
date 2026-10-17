import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_QueryScene-level-1-3_0", "level": 1, "dialogue_id": "QueryScene-level-1-3", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryScene\\", \\"description\\": \\"This API queries a scene of smart home system, given the scene name\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the scene.\\"}}, \\"output_parameters\\": {\\"devices\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of smart devices, containing the name and description.\\"}}}", "dialogue_history": [], "expected_api_name": "QueryScene", "expected_param_dict": {"name": "Morning Routine"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"QueryScene\\", \\"description\\": \\"This API queries a scene of smart home system, given the scene name\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the scene.\\"}}, \\"output_parameters\\": {\\"devices\\": {\\"type\\": \\"list\\", \\"description\\": \\"The list of smart devices, containing the name and description.\\"}}}\\n\\nUser: Can you tell me about the devices included in the Morning Routine scene?\\nAI: Sure, what is the name of the scene you want to know about?\\nUser: Morning Routine\\nGenerate API Request:"}'))
_generated_api_call = "[QueryScene(name='Morning Routine')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn, output)
