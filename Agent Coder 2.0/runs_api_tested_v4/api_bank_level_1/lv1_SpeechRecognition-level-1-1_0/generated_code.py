import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_SpeechRecognition-level-1-1_0", "level": 1, "dialogue_id": "SpeechRecognition-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SpeechRecognition\\", \\"description\\": \\"This API recognizes the speech from a given audio url.\\", \\"input_parameters\\": {\\"url\\": {\\"type\\": \\"str\\", \\"description\\": \\"The url to download the audio. It should end with .wav.\\"}}, \\"output_parameters\\": {\\"transcript\\": {\\"type\\": \\"str\\", \\"description\\": \\"The transcript of the audio.\\"}}}", "dialogue_history": [], "expected_api_name": "SpeechRecognition", "expected_param_dict": {"url": "https://example.com/voice22.wav"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"SpeechRecognition\\", \\"description\\": \\"This API recognizes the speech from a given audio url.\\", \\"input_parameters\\": {\\"url\\": {\\"type\\": \\"str\\", \\"description\\": \\"The url to download the audio. It should end with .wav.\\"}}, \\"output_parameters\\": {\\"transcript\\": {\\"type\\": \\"str\\", \\"description\\": \\"The transcript of the audio.\\"}}}\\n\\nUser: Can you recognize speech from an audio URL?\\nAI: Yes, I can. Which URL should I use?\\nUser: https://example.com/voice22.wav.\\nAI: Okay, let me recognize the speech.\\nGenerate API Request:"}'))
_generated_api_call = "[SpeechRecognition(url='https://example.com/voice22.wav')]"

_expected_api_call = "[SpeechRecognition(url='https://example.com/voice22.wav')]"
_wrong_api_call = "[DefinitelyNotSpeechRecognition(url='https://example.com/voice22.wav')]"
_wrong_params_call = "[SpeechRecognition(url='__different_value_for_test__')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
