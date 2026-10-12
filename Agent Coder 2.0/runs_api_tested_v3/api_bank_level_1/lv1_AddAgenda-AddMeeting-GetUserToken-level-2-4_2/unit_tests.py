from evaluation.api_bank_evaluator import evaluate_api_bank

# The turn object used in the task context
_api_bank_turn = {
    "task_id": "lv1_AddAgenda-AddMeeting-GetUserToken-level-2-4",
    "level": 1,
    "dialogue_id": "AddAgenda-AddMeeting-GetUserToken-level-2-4",
    "turn_id": 2,
    "api_descriptions": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n"
        "The current year is 2023.\n"
        "Input:\n"
        "User: User's utterence\n"
        "AI: AI's response\n"
        "\nExpected output:\n"
        "API-Request: [ApiName(key1='value1', key2='value2', ...)]\n"
        "API descriptions:\n{\"name\": \"GetUserToken\", \"description\": \"Get the user token by username and password.\", ..."
    ),
    "dialogue_history": [],
    "expected_api_name": "AddAgenda",
    "expected_param_dict": {
        "token": "a9s8d7f6g5h4j3k2l1",
        "content": "Meeting with clients at ABC company",
        "time": "2023-12-15 14:00:00",
        "location": "ABC company"
    },
    "prompt": "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] based on the previous dialogue context.\nThe current year is 2023.\nInput: \nUser: User's utterence\nAI: AI's response\n\nExpected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\nAPI descriptions: ..."
}

def _generated_api_call():
    """Simulate the API call generation that would be made."""
    return "[AddAgenda(token='a9s8d7f6g5h4j3k2l1', content='Meeting with clients', time='2023-12-15 14:00:00', location='ABC company')]"

def api_call():
    return _generated_api_call

def evaluate_api_call(candidate=None):
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn, output)

# Test 1: Success case - valid AddAgenda call with all required parameters
def test_addagenda_success():
    """Valid AddAgenda API call should pass evaluation."""
    result = evaluate_api_call()
    # The evaluator should return True (or a positive indicator) for a valid call
    # We assume the evaluator returns a boolean indicating success
    assert result == True, f"Expected True for valid AddAgenda call, got {result}"

# Test 2: Case-insensitive API name matching
def test_case_insensitive_api_name():
    """Different casings of the API name should still match AddAgenda."""
    # Test lowercase
    result_lower = evaluate_api_call("[addagenda(token='x', content='c', time='2023-01-01', location='test')]")
    # Test uppercase
    result_upper = evaluate_api_call("[ADDAGENDA(token='x', content='c', time='2023-01-01', location='test')]")
    # Test mixed case
    result_mixed = evaluate_api_call("[AddAgenda(token='x', content='c', time='2023-01-01', location='test')]")

    # All should pass (return True)
    assert result_lower == True, f"Lowercase API name failed: {result_lower}"
    assert result_upper == True, f"Uppercase API name failed: {result_upper}"
    assert result_mixed == True, f"Mixed-case API name failed: {result_mixed}"

# Test 3: Missing required parameters should fail
def test_missing_token_parameter():
    """Call missing the required 'token' parameter should fail."""
    bad_call = "[AddAgenda(content='c', time='2023-01-01', location='test')]"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for missing token, got {result}"

def test_missing_content_parameter():
    """Call missing the required 'content' parameter should fail."""
    bad_call = "[AddAgenda(token='x', time='2023-01-01', location='test')]"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for missing content, got {result}"

def test_missing_time_parameter():
    """Call missing the required 'time' parameter should fail."""
    bad_call = "[AddAgenda(token='x', content='c', location='test')]"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for missing time, got {result}"

def test_missing_location_parameter():
    """Call missing the required 'location' parameter should fail."""
    bad_call = "[AddAgenda(token='x', content='c', time='2023-01-01')]"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for missing location, got {result}"

# Test 4: Invalid date format should fail
def test_invalid_date_format():
    """A time string with incorrect format should cause evaluation to fail."""
    bad_call = "[AddAgenda(token='x', content='c', time='2023-13-45 25:00:00', location='test')]"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for invalid date format, got {result}"

# Test 5: Non-existent API name should fail
def test_non_existent_api_name():
    """Using a completely different API name should fail."""
    bad_call = "[Payments(amount=100))]"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for non-existent API, got {result}"

# Test 6: Malformed API call (missing brackets, invalid syntax)
def test_malformed_api_call():
    """Completely malformed API call string should fail."""
    bad_call = "AddAgenda(token='x', content='c', time='2023-01-01', location='test'"
    result = evaluate_api_call(bad_call)
    assert result == False, f"Expected False for malformed call, got {result}"

# Test 7: Whitespace variations should be normalized correctly
def test_whitespace_normalization():
    """Whitespace variations in the call should still parse correctly."""
    # Extra spaces around commas and colons
    call_with_spaces = "[AddAgenda   (token='x'   ,   content='c'   ,   time='2023-01-01'   ,   location='test')]"
    result = evaluate_api_call(call_with_spaces)
    assert result == True, f"Expected True for whitespace-normalized call, got {result}"

if __name__ == "__main__":
    test_addagenda_success()
    test_case_insensitive_api_name()
    test_missing_token_parameter()
    test_missing_content_parameter()
    test_missing_time_parameter()
    test_missing_location_parameter()
    test_invalid_date_format()
    test_non_existent_api_name()
    test_malformed_api_call()
    test_whitespace_normalization()
    print("All tests passed!")
