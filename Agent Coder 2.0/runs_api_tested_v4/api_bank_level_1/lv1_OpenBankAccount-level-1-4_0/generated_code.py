import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_OpenBankAccount-level-1-4_0", "level": 1, "dialogue_id": "OpenBankAccount-level-1-4", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"OpenBankAccount\\", \\"description\\": \\"This is an API for opening a bank account for a user, given the account, password and name.\\", \\"input_parameters\\": {\\"account\\": {\\"type\\": \\"str\\", \\"description\\": \\"The account for the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password.\\"}, \\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"account holder name.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"success or failed\\"}}}", "dialogue_history": [], "expected_api_name": "OpenBankAccount", "expected_param_dict": {"account": "12345678", "password": "p@ssw0rd123!", "name": "John Smith"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"OpenBankAccount\\", \\"description\\": \\"This is an API for opening a bank account for a user, given the account, password and name.\\", \\"input_parameters\\": {\\"account\\": {\\"type\\": \\"str\\", \\"description\\": \\"The account for the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password.\\"}, \\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"account holder name.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"success or failed\\"}}}\\n\\nUser: Can you help me open a bank account?\\nAI: Sure, I can help you with that. What account number would you like to use?\\nUser: 12345678\\nAI: And what password would you like to use for this account?\\nUser: p@ssw0rd123!\\nAI: Lastly, what is your full name?\\nUser: John Smith\\nGenerate API Request:"}'))
_generated_api_call = "[OpenBankAccount(account='12345678', password='p@ssw0rd123!', name='John Smith')]"

_expected_api_call = "[OpenBankAccount(account='12345678', password='p@ssw0rd123!', name='John Smith')]"
_wrong_api_call = "[DefinitelyNotOpenBankAccount(account='12345678', password='p@ssw0rd123!', name='John Smith')]"
_wrong_params_call = "[OpenBankAccount(account='__different_value_for_test__', password='p@ssw0rd123!', name='John Smith')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
