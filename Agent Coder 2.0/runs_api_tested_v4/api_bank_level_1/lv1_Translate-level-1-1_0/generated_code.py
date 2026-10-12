import json
from dataset.api_bank_loader import APIBankTurn
from evaluation.api_bank_evaluator import evaluate_api_bank

_api_bank_turn = APIBankTurn(**json.loads('{"task_id": "lv1_Translate-level-1-1_0", "level": 1, "dialogue_id": "Translate-level-1-1", "turn_id": 0, "api_descriptions": "\\nGenerate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Translate\\", \\"description\\": \\"The API for translating text from source language to target language.\\", \\"input_parameters\\": {\\"src\\": {\\"type\\": \\"str\\", \\"description\\": \\"The text to be translated.\\"}, \\"src_lang\\": {\\"type\\": \\"str\\", \\"description\\": \\"[Optional] The source language to translate from. Default is auto.\\"}, \\"tgt_lang\\": {\\"type\\": \\"str\\", \\"description\\": \\"[Optional] The target language to translate to. Default is english/en.\\"}}, \\"output_parameters\\": {\\"translated_text\\": {\\"type\\": \\"str\\", \\"description\\": \\"The translated text.\\"}}}", "dialogue_history": [], "expected_api_name": "Translate", "expected_param_dict": {"src": "Hello, how are you?", "tgt_lang": "fr"}, "prompt": "Generate an API request in the format of [ApiName(key1=\'value1\', key2=\'value2\', ...)] based on the previous dialogue context.\\nThe current year is 2023.\\nInput: \\nUser: User\'s utterence\\nAI: AI\'s response\\n\\nExpected output:\\nAPI-Request: [ApiName(key1=\'value1\', key2=\'value2\', ...)]\\n\\nAPI descriptions:\\n{\\"name\\": \\"Translate\\", \\"description\\": \\"The API for translating text from source language to target language.\\", \\"input_parameters\\": {\\"src\\": {\\"type\\": \\"str\\", \\"description\\": \\"The text to be translated.\\"}, \\"src_lang\\": {\\"type\\": \\"str\\", \\"description\\": \\"[Optional] The source language to translate from. Default is auto.\\"}, \\"tgt_lang\\": {\\"type\\": \\"str\\", \\"description\\": \\"[Optional] The target language to translate to. Default is english/en.\\"}}, \\"output_parameters\\": {\\"translated_text\\": {\\"type\\": \\"str\\", \\"description\\": \\"The translated text.\\"}}}\\n\\nUser: Can you translate \\"Hello, how are you?\\" to French?\\nAI: Sure, I can do that.\\nGenerate API Request:"}'))
_generated_api_call = "[ApiName(key1='src', key2='Hello, how are you?', key3='tgt_lang', key4='French')]"

_expected_api_call = "[Translate(src='Hello, how are you?', tgt_lang='fr')]"
_wrong_api_call = "[DefinitelyNotTranslate(src='Hello, how are you?', tgt_lang='fr')]"
_wrong_params_call = "[Translate(src='__different_value_for_test__', tgt_lang='fr')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None, turn=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn if turn is None else turn, output)
