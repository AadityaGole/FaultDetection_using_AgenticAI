import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_PlayMusic-level-1-3_0", "level": 1, "dialogue_id": "PlayMusic-level-1-3", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"PlayMusic\\", \\"description\\": \\"This API triggers a music player to play music.\\", \\"input_parameters\\": {\\"music_name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the music to play.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The corresponding url scheme to trigger the music player.\\"}}}", "dialogue_history": [], "expected_api_name": "PlayMusic", "expected_param_dict": {"music_name": "Shape of You"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"PlayMusic\\", \\"description\\": \\"This API triggers a music player to play music.\\", \\"input_parameters\\": {\\"music_name\\": {\\"type\\": \\"str\\", \\"description\\": \\"The name of the music to play.\\"}}, \\"output_parameters\\": {\\"status\\": {\\"type\\": \\"str\\", \\"description\\": \\"The corresponding url scheme to trigger the music player.\\"}}}\\n\\nUser: Can you play the music \\"Shape of You\\"?\\nAI: Sure, I can play \\"Shape of You\\".\\nGenerate API Request:"}'))
_generated_api_call = "[PlayMusic(music_name='Shape of You')]"

_expected_api_call = "[PlayMusic(music_name='Shape of You')]"
_wrong_api_call = "[DefinitelyNotPlayMusic(music_name='Shape of You')]"
_wrong_params_call = "[PlayMusic(music_name='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
