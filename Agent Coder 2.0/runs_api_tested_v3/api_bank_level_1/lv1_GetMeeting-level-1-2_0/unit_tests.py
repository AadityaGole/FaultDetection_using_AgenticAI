from evaluate.api_bank_evaluator import evaluate_api_bank

# The ground truth from the task
EXPECTED_API_NAME = "GetUserToken"
EXPECTED_PARAM_DICT = {"username": "JohnDoe", "password": "pass123"}

def _generate_correct_call():
    """Generate the correct API call string for the GetUserToken API."""
    return f"GetUserToken(username='JohnDoe', password='pass123')"

def _generate_case_insensitive_call():
    """Generate the same call with different casing for case-insensitivity test."""
    # The evaluator should treat "getusertoken" as equivalent to "GetUserToken"
    return "getusertoken(username='JohnDoe', password='pass123')"

def _generate_missing_params_call():
    """Call with missing required parameters."""
    return "GetUserToken(password='pass123')"

def _generate_wrong_api_name_call():
    """Call with a non-existent API name."""
    return "NonExistentAPI(username='JohnDoe', password='pass123')"

def _generate_extra_param_call():
    """Call with an unexpected extra parameter."""
    return "GetUserToken(username='JohnDoe', password='pass123', role='admin')"

def _generate_empty_string_params_call():
    """Call with empty string values for required parameters."""
    return "GetUserToken(username='', password='')"

def _generate_invalid_date_format_call():
    """Call with invalid date format (not %Y-%m-%d %H:%M:%S)."""
    # This would be tricky since the API doesn't take dates directly,
    # but we can still test that the evaluator handles type mismatches
    return "GetUserToken(username='JohnDoe', password='pass123', start_time='2023-13-01 25:00:00')"

# Test 1: Happy path - correct API call with proper parameters
def test_successful_getusertoken_call():
    """Test that a correctly formed GetUserToken call passes evaluation."""
    call_str = _generate_correct_call()
    result = evaluate_api_call(call_str)

    # The evaluator should return True (or similar positive indicator) for a valid call
    # Based on the task description, successful evaluation means all four conditions passed
    assert result is True, f"Expected True for valid call, got {result}"

# Test 2: Case-insensitive API name matching
def test_case_insensitive_api_name():
    """Test that the evaluator treats GetUserToken and getusertoken as equivalent."""
    call_str = _generate_case_insensitive_call()
    result = evaluate_api_call(call_str)
    assert result is True, f"Case-insensitive match failed for '{call_str}'. Expected True."

# Test 3: Missing required parameters should fail
def test_missing_username():
    """Test that missing username parameter causes failure."""
    call_str = _generate_missing_params_call()
    result = evaluate_api_call(call_str)
    assert result is False, f"Missing username should cause failure, got {result}"

# Test 4: Missing required parameters with empty strings should fail
def test_empty_required_params():
    """Test that empty string values for required parameters cause failure."""
    call_str = _generate_empty_string_params_call()
    result = evaluate_api_call(call_str)
    assert result is False, f"Empty string parameters should cause failure, got {result}"

# Test 5: Wrong API name should fail
def test_wrong_api_name():
    """Test that a non-existent API name fails evaluation."""
    call_str = _generate_wrong_api_name_call()
    result = evaluate_api_call(call_str)
    assert result is False, f"Wrong API name should cause failure, got {result}"

# Test 6: Extra parameters beyond what's expected should fail
def test_extra_parameters():
    """Test that additional unexpected parameters cause failure."""
    call_str = _generate_extra_param_call()
    result = evaluate_api_call(call_str)
    assert result is False, f"Extra parameters should cause failure, got {result}"

# Test 7: Invalid date format (if the API had date parameters) - though our API doesn't
# Since GetUserToken doesn't have date parameters, we test with a malformed string
# that might trigger type checking in the evaluator
def test_invalid_input_format():
    """Test handling of malformed input that doesn't match expected schema."""
    call_str = _generate_invalid_date_format_call()
    result = evaluate_api_call(call_str)
    # Should fail because the string doesn't match the expected API request format
    assert result is False, f"Malformed call should cause failure, got {result}"

# Test 8: Verify the correct API name is used (case-insensitive match)
def test_api_name_normalization():
    """Verify that the evaluator normalizes API names case-insensitively."""
    call_str = _generate_case_insensitive_call()
    result = evaluate_api_call(call_str)
    assert result is True, f"Normalized API name 'getusertoken' should pass, got {result}"
