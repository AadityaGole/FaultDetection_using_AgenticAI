import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_OpenBankAccount-level-1-5_0", "level": 1, "dialogue_id": "OpenBankAccount-level-1-5", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"OpenBankAccount\\", \\"description\\": \\"This is an API for opening a bank account for a user, given the account, password and name.\\", \\"input_parameters\\": {\\"account\\": {\\"type\\": \\"str\\", \\"description\\": \\"The account for the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password.\\"}, \\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"account holder name.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"success or failed\\"}}}", "dialogue_history": [], "expected_api_name": "OpenBankAccount", "expected_param_dict": {"account": "My New Account", "password": "password123", "name": "John"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"OpenBankAccount\\", \\"description\\": \\"This is an API for opening a bank account for a user, given the account, password and name.\\", \\"input_parameters\\": {\\"account\\": {\\"type\\": \\"str\\", \\"description\\": \\"The account for the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password.\\"}, \\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"account holder name.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"success or failed\\"}}}\\n\\nUser: Can you help me open a bank account?\\nAI: Sure, I can help with that. To open a bank account, I\'ll just need some information from you. What would you like to name the account?\\nUser: Let\'s name it \\"My New Account\\".\\nAI: Great, \\"My New Account\\". What password would you like to use for the account?\\nUser: \\"password123\\".\\nAI: And finally, what\'s your name?\\nUser: My name is John.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='My New Account', key2='password123', key3='John')]"

_expected_api_call = "[OpenBankAccount(account='My New Account', password='password123', name='John')]"
_wrong_api_call = "[DefinitelyNotOpenBankAccount(account='My New Account', password='password123', name='John')]"
_wrong_params_call = "[OpenBankAccount(account='__different_value_for_test__', password='password123', name='John')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
