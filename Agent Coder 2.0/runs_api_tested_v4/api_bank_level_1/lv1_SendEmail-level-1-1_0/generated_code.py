import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_SendEmail-level-1-1_0", "level": 1, "dialogue_id": "SendEmail-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SendEmail\\", \\"description\\": \\"This API for sending email, given the receiver, subject and content.\\", \\"input_parameters\\": {\\"receiver\\": {\\"type\\": \\"str\\", \\"description\\": \\"The receiver address of the email.\\"}, \\"subject\\": {\\"type\\": \\"str\\", \\"description\\": \\"The subject address of the email.\\"}, \\"content\\": {\\"type\\": \\"str\\", \\"description\\": \\"The content of the email.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The status of the email.\\"}}}", "dialogue_history": [], "expected_api_name": "SendEmail", "expected_param_dict": {"receiver": "john@example.com", "subject": "Meeting Reminder", "content": "Don"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SendEmail\\", \\"description\\": \\"This API for sending email, given the receiver, subject and content.\\", \\"input_parameters\\": {\\"receiver\\": {\\"type\\": \\"str\\", \\"description\\": \\"The receiver address of the email.\\"}, \\"subject\\": {\\"type\\": \\"str\\", \\"description\\": \\"The subject address of the email.\\"}, \\"content\\": {\\"type\\": \\"str\\", \\"description\\": \\"The content of the email.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The status of the email.\\"}}}\\n\\nUser: Can you help me send an email to john@example.com with subject \\"Meeting Reminder\\" and content \\"Don\'t forget our meeting tomorrow at 2pm.\\"?\\nAI: Sure, I can help you with that.\\nGenerate API Request:"}'))
_generated_api_call = "[SendEmail(receiver='john@example.com', subject='Meeting Reminder', content='Don\\'t forget our meeting tomorrow at 2pm.')]"

_expected_api_call = "[SendEmail(receiver='john@example.com', subject='Meeting Reminder', content='Don')]"
_wrong_api_call = "[DefinitelyNotSendEmail(receiver='john@example.com', subject='Meeting Reminder', content='Don')]"
_wrong_params_call = "[SendEmail(receiver='__different_value_for_test__', subject='Meeting Reminder', content='Don')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
