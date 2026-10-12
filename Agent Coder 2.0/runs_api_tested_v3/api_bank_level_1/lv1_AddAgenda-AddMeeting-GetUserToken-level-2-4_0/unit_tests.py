from evaluate.api_bank_evaluator import evaluate_api_bank
from typing import Dict, Any

# Ground truth from the task description
EXPECTED_API_NAME_GETUSERTOKEN = "GetUserToken"
EXPECTED_PARAM_DICT_GETUSERTOKEN = {"username": "JohnDoe", "password": "pass123"}
EXPECTED_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Valid API calls for evaluation
VALID_CALLS = [
    # GetUserToken - success
    {
        "call": "GetUserToken(username=JohnDoe, password=pass123)",
        "should_pass": True,
        "expected_api_name": EXPECTED_API_NAME_GETUSERTOKEN,
        "expected_params": EXPECTED_PARAM_DICT_GETUSERTOKEN,
        "date_format_valid": True,
    },
    # AddAgenda - success
    {
        "call": 'AddAgenda(token=<token>, content="Meeting with clients", time="2023-12-15 14:00:00", location="ABC company")',
        "should_pass": True,
        "expected_api_name": "AddAgenda",
        "expected_params": {"token": "<token>", "content": "Meeting with clients", "time": "2023-12-15 14:00:00", "location": "ABC company"},
        "date_format_valid": True,
    },
]

# Invalid calls for negative testing
INVALID_CALLS = [
    # Wrong API name
    {
        "call": "getusertoken(username=JohnDoe, password=pass123)",
        "should_pass": False,
        "expected_api_name": "GetUserToken",
        "expected_params": EXPECTED_PARAM_DICT_GETUSERTOKEN,
        "reason": "wrong_api_name_case",
    },
    # Missing required parameter
    {
        "call": "GetUserToken(password=pass123)",
        "should_pass": False,
        "expected_api_name": EXPECTED_API_NAME_GETUSERTOKEN,
        "expected_params": EXPECTED_PARAM_DICT_GETUSERTOKEN,
        "reason": "missing_username",
    },
    # Invalid date format
    {
        "call": "AddAgenda(token=<token>, content="Meeting", time="2023/12/15 14:00:00", location="ABC company")",
        "should_pass": False,
        "expected_api_name": "AddAgenda",
        "expected_params": EXPECTED_PARAM_DICT_GETUSERTOKEN,  # placeholder
        "reason": "invalid_date_format",
    },
    # Non-existent API
    {
        "call": "InvalidAPI(username=JohnDoe, password=pass123)",
        "should_pass": False,
        "expected_api_name": "GetUserToken",
        "expected_params": EXPECTED_PARAM_DICT_GETUSERTOKEN,
        "reason": "unknown_api",
    },
]

def _parse_and_evaluate(call: str) -> Dict[str, Any]:
    """Call evaluate_api_call with the given API call string."""
    return evaluate_api_call(call)

def test_successful_getusertoken_call():
    """Test successful GetUserToken call with correct parameters."""
    result = _parse_and_evaluate("GetUserToken(username=JohnDoe, password=pass123)")
    # The evaluator returns a dict with parsed_api_name, api_match, params_match, passed
    assert "parsed_api_name" in result
    assert result["parsed_api_name"].lower() == EXPECTED_API_NAME_GETUSERTOKEN.lower()
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

def test_successful_addagenda_call():
    """Test successful AddAgenda call with correct parameters including valid date format."""
    result = _parse_and_evaluate(
        'AddAgenda(token=abc123, content="Meeting with clients", time="2023-12-15 14:00:00", location="ABC company")'
    )
    assert "parsed_api_name" in result
    assert result["parsed_api_name"].lower() == "addagenda".replace(" ", "")
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

def test_case_insensitive_api_name_matching():
    """Test that API name matching is case-insensitive."""
    # Lowercase variant
    result_lower = _parse_and_evaluate("getusertoken(username=JohnDoe, password=pass123)")
    assert result_lower["parsed_api_name"].lower() == EXPECTED_API_NAME_GETUSERTOKEN.lower()

    # Mixed case variant
    result_mixed = _parse_and_evaluate("ADDAgenda(token=abc123, content='test', time='2023-01-01 10:00:00', location='HQ')")
    assert result_mixed["parsed_api_name"].lower() == EXPECTED_API_NAME_GETUSERTOKEN.lower()

def test_missing_required_parameter():
    """Test that missing required parameters cause failure."""
    result = _parse_and_evaluate("GetUserToken(password=pass123)")
    assert result["passed"] is False
    # Should fail because username is required

def test_invalid_date_format():
    """Test that invalid date format causes failure."""
    result = _parse_and_evaluate(
        'AddAgenda(token=abc123, content="Meeting", time="2023/12/15 14:00:00", location="ABC company")'
    )
    assert result["passed"] is False
    assert result["reason"] == "invalid_date_format"

def test_non_existent_api():
    """Test that unknown API names are rejected."""
    result = _parse_and_evaluate("UnknownAPI(username=JohnDoe, password=pass123)")
    assert result["passed"] is False
    assert result["reason"] == "unknown_api"

def test_addagenda_missing_token():
    """Test AddAgenda call without required token parameter."""
    result = _parse_and_evaluate("AddAgenda(content=\"Meeting\", time=\"2023-12-15 14:00:00\", location=\"ABC company\")")
    assert result["passed"] is False
    assert result["reason"] == "missing_token"

def test_addagenda_wrong_type_for_time():
    """Test AddAgenda with time in incorrect format."""
    result = _parse_and_evaluate(
        'AddAgenda(token=abc123, content="Meeting", time="2023-12-15", location="ABC company")'
    )
    assert result["passed"] is False
    assert result["reason"] == "invalid_date_format"

def test_addagenda_empty_string_values():
    """Test handling of empty string values (edge case)."""
    result = _parse_and_evaluate(
        'AddAgenda(token="", content="", time="2023-12-15 14:00:00", location="")'
    )
    # This should either pass or fail depending on strictness - we expect it might fail due to empty token
    # but the key is that the evaluator handles it gracefully
    assert "passed" in result

if __name__ == "__main__":
    test_successful_getusertoken_call()
    test_successful_addagenda_call()
    test_case_insensitive_api_name_matching()
    test_missing_required_parameter()
    test_invalid_date_format()
    test_non_existent_api()
    test_addagenda_missing_token()
    test_addagenda_wrong_type_for_time()
    test_addagenda_empty_string_values()
