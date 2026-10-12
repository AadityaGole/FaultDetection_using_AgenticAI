import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_OpenBankAccount-level-1-2_0", "level": 1, "dialogue_id": "OpenBankAccount-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"OpenBankAccount\\", \\"description\\": \\"This is an API for opening a bank account for a user, given the account, password and name.\\", \\"input_parameters\\": {\\"account\\": {\\"type\\": \\"str\\", \\"description\\": \\"The account for the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password.\\"}, \\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"account holder name.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"success or failed\\"}}}", "dialogue_history": [], "expected_api_name": "OpenBankAccount", "expected_param_dict": {"account": "johndoe123", "password": "mypass123", "name": "John Doe"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"OpenBankAccount\\", \\"description\\": \\"This is an API for opening a bank account for a user, given the account, password and name.\\", \\"input_parameters\\": {\\"account\\": {\\"type\\": \\"str\\", \\"description\\": \\"The account for the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password.\\"}, \\"name\\": {\\"type\\": \\"str\\", \\"description\\": \\"account holder name.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"success or failed\\"}}}\\n\\nUser: Can you help me open a bank account?\\nAI: Sure, I can assist you with that. What account identifier would you like to use?\\nUser: My chosen account identifier is \\"johndoe123\\"\\nAI: Great! What password would you like to use for this account?\\nUser: \\"mypass123\\"\\nAI: And what is the name of the account holder?\\nUser: John Doe\\nAI: Thank you. Let me go ahead and open this bank account for you.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='account', key2='johndoe123', key3='password', key4='mypass123', key5='name', key6='John Doe')]"

_expected_api_call = "[OpenBankAccount(account='johndoe123', password='mypass123', name='John Doe')]"
_wrong_api_call = "[DefinitelyNotOpenBankAccount(account='johndoe123', password='mypass123', name='John Doe')]"
_wrong_params_call = "[OpenBankAccount(account='__different_value_for_test__', password='mypass123', name='John Doe')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
