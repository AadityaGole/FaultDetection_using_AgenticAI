from evaluate.api_bank_evaluator import evaluate_api_bank

# The ground truth from the task defines the expected API call structure
# For the AddAgenda API with the given parameters
EXPECTED_API_CALL = "[AddAgenda(token='a9s8d7f6g5h4j3k2l1', content='Meeting with clients', time='2023-12-15 14:00:00', location='ABC company')]"

def test_addagenda_success():
    """Test successful evaluation of a valid AddAgenda API call."""
    # This simulates the candidate being the generated API call string
    result = evaluate_api_call(EXPECTED_API_CALL)
    # The evaluator should return True for a valid call with correct parameters
    assert result is True

def test_addagenda_missing_token():
    """Test that missing required token parameter causes failure."""
    incomplete_call = "[AddAgenda(content='Meeting', time='2023-12-15 14:00:00', location='ABC company')]"
    result = evaluate_api_call(incomplete_call)
    assert result is False

def test_addagenda_wrong_api_name():
    """Test that a different API name fails the case-insensitive match."""
    wrong_api_call = "[GetUserToken(token='a9s8d7f6g5h4j3k2l1', content='Meeting', time='2023-12-15 14:00:00', location='ABC company')]"
    result = evaluate_api_call(wrong_api_call)
    assert result is False

def test_addagenda_invalid_time_format():
    """Test that an unrecognized date format fails the parser."""
    invalid_time_call = "[AddAgenda(token='a9s8d7f6g5h4j3k2l1', content='Meeting', time='2023-13-01 25:00:00', location='ABC company')]"
    result = evaluate_api_call(invalid_time_call)
    assert result is False

def test_addagenda_malformed_syntax():
    """Test that syntactically invalid API calls fail."""
    malformed_call = "AddAgenda(token='a9s8d7f6g5h4j3k2l1', content='Meeting'"  # missing closing bracket
    result = evaluate_api_call(malformed_call)
    assert result is False

def test_getuser_token_success():
    """Test successful evaluation of GetUserToken API call."""
    get_user_call = "[GetUserToken(username='JohnDoe', password='pass123')]->{'token': 'a9s8d7f6g5h4j3k2l1'}"
    result = evaluate_api_call(get_user_call)
    assert result is True

def test_getuser_token_missing_password():
    """Test that missing password parameter causes failure."""
    incomplete_get_user = "[GetUserToken(username='JohnDoe')]"
    result = evaluate_api_call(incomplete_get_user)
    assert result is False

def test_getuser_token_wrong_api_name():
    """Test that calling GetUserToken with wrong casing fails."""
    wrong_case_call = "[getusertoken(username='JohnDoe', password='pass123')]"
    result = evaluate_api_call(wrong_case_call)
    assert result is False

if __name__ == "__main__":
    test_addagenda_success()
    test_addagenda_missing_token()
    test_addagenda_wrong_api_name()
    test_addagenda_invalid_time_format()
    test_addagenda_malformed_syntax()
    test_getuser_token_success()
    test_getuser_token_missing_password()
    test_getuser_token_wrong_api_name()
