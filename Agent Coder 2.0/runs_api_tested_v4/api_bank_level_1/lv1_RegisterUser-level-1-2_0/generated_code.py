import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_RegisterUser-level-1-2_0", "level": 1, "dialogue_id": "RegisterUser-level-1-2", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"RegisterUser\\", \\"description\\": \\"The API for registering a account, given the username, password and email.\\", \\"input_parameters\\": {\\"username\\": {\\"type\\": \\"str\\", \\"description\\": \\"The username of the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password of the user.\\"}, \\"email\\": {\\"type\\": \\"str\\", \\"description\\": \\"The email of the user.\\"}}, \\"output_parameters\\": {\\"token\\": {\\"type\\": \\"str\\", \\"description\\": \\"The token of the user.\\"}}}", "dialogue_history": [], "expected_api_name": "RegisterUser", "expected_param_dict": {"username": "johndoe", "password": "mypassword123", "email": "johndoe@email.com"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"RegisterUser\\", \\"description\\": \\"The API for registering a account, given the username, password and email.\\", \\"input_parameters\\": {\\"username\\": {\\"type\\": \\"str\\", \\"description\\": \\"The username of the user.\\"}, \\"password\\": {\\"type\\": \\"str\\", \\"description\\": \\"The password of the user.\\"}, \\"email\\": {\\"type\\": \\"str\\", \\"description\\": \\"The email of the user.\\"}}, \\"output_parameters\\": {\\"token\\": {\\"type\\": \\"str\\", \\"description\\": \\"The token of the user.\\"}}}\\n\\nUser: Can you help me register for an account on this platform?\\nAI: Sure, I can help you with that. What would you like your username to be?\\nUser: My preferred username is \\"johndoe\\".\\nAI: Great! What would you like your password to be?\\nUser: How about \\"mypassword123\\"?\\nAI: Okay, and what is your email address?\\nUser: It\'s johndoe@email.com.\\nGenerate API Request:"}'))
_generated_api_call = "[RegisterUser(username='johndoe', password='mypassword123', email='johndoe@email.com')]"

_expected_api_call = "[RegisterUser(username='johndoe', password='mypassword123', email='johndoe@email.com')]"
_wrong_api_call = "[DefinitelyNotRegisterUser(username='johndoe', password='mypassword123', email='johndoe@email.com')]"
_wrong_params_call = "[RegisterUser(username='__different_value_for_test__', password='mypassword123', email='johndoe@email.com')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
