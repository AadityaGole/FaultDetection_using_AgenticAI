import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_Calculator-level-1-2_0", "level": 1, "dialogue_id": "Calculator-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Calculator\\", \\"description\\": \\"This API provides basic arithmetic operations: addition, subtraction, multiplication, and division.\\", \\"input_parameters\\": {\\"formula\\": {\\"type\\": \\"str\\", \\"description\\": \\"The formula that needs to be calculated. Only integers are supported. Valid operators are +, -, *, /, and (, ). For example, \'(1 + 2) * 3\'.\\"}}, \\"output_parameters\\": {\\"result\\": {\\"type\\": \\"float\\", \\"description\\": \\"The result of the formula.\\"}}}", "dialogue_history": [], "expected_api_name": "Calculator", "expected_param_dict": {"formula": "(5+3)*6"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Calculator\\", \\"description\\": \\"This API provides basic arithmetic operations: addition, subtraction, multiplication, and division.\\", \\"input_parameters\\": {\\"formula\\": {\\"type\\": \\"str\\", \\"description\\": \\"The formula that needs to be calculated. Only integers are supported. Valid operators are +, -, *, /, and (, ). For example, \'(1 + 2) * 3\'.\\"}}, \\"output_parameters\\": {\\"result\\": {\\"type\\": \\"float\\", \\"description\\": \\"The result of the formula.\\"}}}\\n\\nUser: Can you perform some basic arithmetic calculation for me?\\nAI: Sure, what calculation do you want me to perform?\\nUser: What is the result of (5+3)*6?\\nGenerate API Request:"}'))
_generated_api_call = "[Calculator(key1='(5+3)*6')]"

_expected_api_call = "[Calculator(formula='(5+3)*6')]"
_wrong_api_call = "[DefinitelyNotCalculator(formula='(5+3)*6')]"
_wrong_params_call = "[Calculator(formula='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
