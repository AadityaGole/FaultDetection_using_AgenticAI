import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_ImageCaption-level-1-1_0", "level": 1, "dialogue_id": "ImageCaption-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ImageCaption\\", \\"description\\": \\"This API generates a caption for a given image.\\", \\"input_parameters\\": {\\"url\\": {\\"type\\": \\"str\\", \\"description\\": \\"The url to download the image. It should end with .jpg, .jpeg or .png.\\"}}, \\"output_parameters\\": {\\"caption\\": {\\"type\\": \\"str\\", \\"description\\": \\"The generated caption.\\"}}}", "dialogue_history": [], "expected_api_name": "ImageCaption", "expected_param_dict": {"url": "http://l7.alamy.com/zooms/278b12a987734ec285da7155397e0d0a/an-airplane-takes-off-from-terminal-1-at-manchester-international-h4b040.jpg"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"ImageCaption\\", \\"description\\": \\"This API generates a caption for a given image.\\", \\"input_parameters\\": {\\"url\\": {\\"type\\": \\"str\\", \\"description\\": \\"The url to download the image. It should end with .jpg, .jpeg or .png.\\"}}, \\"output_parameters\\": {\\"caption\\": {\\"type\\": \\"str\\", \\"description\\": \\"The generated caption.\\"}}}\\n\\nUser: Can you describe this image for me?\\nAI: Sure, please provide me with the URL for the image.\\nUser: Here it is: http://l7.alamy.com/zooms/278b12a987734ec285da7155397e0d0a/an-airplane-takes-off-from-terminal-1-at-manchester-international-h4b040.jpg\\nGenerate API Request:"}'))
_generated_api_call = "[ImageCaption(url='http://l7.alamy.com/zooms/278"

_expected_api_call = "[ImageCaption(url='http://l7.alamy.com/zooms/278b12a987734ec285da7155397e0d0a/an-airplane-takes-off-from-terminal-1-at-manchester-international-h4b040.jpg')]"
_wrong_api_call = "[DefinitelyNotImageCaption(url='http://l7.alamy.com/zooms/278b12a987734ec285da7155397e0d0a/an-airplane-takes-off-from-terminal-1-at-manchester-international-h4b040.jpg')]"
_wrong_params_call = "[ImageCaption(url='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
