import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_DeleteScene-level-1-3_0", "level": 1, "dialogue_id": "DeleteScene-level-1-3", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"DeleteScene\\", \\"description\\": \\"This API deletes a scene by its name.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the scene.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the deletion is successful.\\"}}}", "dialogue_history": [], "expected_api_name": "DeleteScene", "expected_param_dict": {"name": "Movie Time"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"DeleteScene\\", \\"description\\": \\"This API deletes a scene by its name.\\", \\"input_parameters\\": {\\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the scene.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"Whether the deletion is successful.\\"}}}\\n\\nUser: Can you help me delete a scene named \\"Movie Time\\"?\\nAI: Sure, I can assist with that. Deleting scene named \\"Movie Time\\".\\nGenerate API Request:"}'))
_generated_api_call = "API-Request: [DeleteScene(name='Movie Time')]"

_expected_api_call = "[DeleteScene(name='Movie Time')]"
_wrong_api_call = "[DefinitelyNotDeleteScene(name='Movie Time')]"
_wrong_params_call = "[DeleteScene(name='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
