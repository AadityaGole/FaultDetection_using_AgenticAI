from evaluate.api_bank_evaluator import evaluate_api_bank
from dataset.api_bank_loader import APIBankTurn

# Setup the turn data from the task context
api_turn = {
    "task_id": "lv1_QueryStock-OpenBankAccount-QueryBalance-GetUserToken-level-2-1",
    "level": 1,
    "dialogue_id": "QueryStock-OpenBankAccount-QueryBalance-GetUserToken-level-2-1",
    "turn_id": 4,
    "api_descriptions": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n\nThe current year is 2023.\n"
        "Input:\nUser: User's utterence\nAI: AI's response\n\nExpected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\nAPI descriptions:\n{\"name\": \"OpenBankAccount\", ...}\n..."
    ),
    "expected_api_name": "GetUserToken",
    "expected_param_dict": {"username": "user4", "password": "user4pass"},
    "prompt": "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] based on the previous dialogue context.\nThe current year is 2023.\nInput:\nUser: User's utterence\nAI: AI's response\n\nExpected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\nAPI descriptions:\n...\n"
}

# Create the APIBankTurn instance
bank_turn = APIBankTurn(**api_turn)

def evaluate_api_call(candidate=None):
    """Wrapper around the actual evaluator call."""
    return evaluate_api_bank(bank_turn, candidate)

# Test 1: Positive case - valid GetUserToken call with correct parameters
result = evaluate_api_call(
    "[GetUserToken(username='user4', password='user4pass')]"
)
assert result["passed"] is True, "Valid GetUserToken call should pass evaluation"

# Test 2: Negative case - wrong API name (should not match GetUserToken)
wrong_api_result = evaluate_api_call(
    "[QueryStock(stock_code='AMZN', date='2022-03-12')]"
)
assert result["passed"] is False, "Wrong API name should fail evaluation"

# Test 3: Negative case - missing required parameters (username/password)
missing_params_result = evaluate_api_call(
    "[GetUserToken()]"
)
assert result["passed"] is False, "Missing required parameters should fail evaluation"

# Test 4: Negative case - extra unexpected parameters (should still pass if core params are correct)
extra_param_result = evaluate_api_call(
    "[GetUserToken(username='user4', password='user4pass', role='admin')]"
)
assert result["passed"] is True, "Extra optional parameters should not cause failure"

# Test 5: Whitespace variation - same call with extra spaces (should pass)
whitespace_result = evaluate_api_call(
    "[GetUserToken( username='user4', password='user4pass' ) ]"
)
assert result["passed"] is True, "Whitespace variations should be handled correctly"

# Test 6: Edge case - empty string for username (boundary value)
empty_username_result = evaluate_api_call(
    "[GetUserToken(username='', password='pass')]"
)
# Depending on the evaluator, this might pass or fail - at minimum it shouldn't crash
# We'll just ensure it doesn't raise an exception and returns a consistent structure
try:
    result = evaluate_api_call("[GetUserToken(username='', password='pass')]")
    assert isinstance(result, dict), "Result should be a dictionary"
except Exception as e:
    assert False, f"Empty username should not raise an exception: {e}"

# Test 7: Edge case - empty string for password
empty_password_result = evaluate_api_call(
    "[GetUserToken(username='user4', password='')]"
)
try:
    result = evaluate_api_call("[GetUserToken(username='user4', password='')]")
    assert isinstance(result, dict), "Result should be a dictionary"
except Exception as e:
    assert False, f"Empty password should not raise an exception: {e}"
