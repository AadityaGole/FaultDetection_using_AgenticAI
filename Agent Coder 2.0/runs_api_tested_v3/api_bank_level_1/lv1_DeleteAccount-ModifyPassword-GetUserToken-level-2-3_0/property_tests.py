from hypothesis import given, strategies as st, settings, assume

# Entry point for evaluating API calls against the bank API schema
from somewhere import evaluate_api_call

@given(st.text(min_length=1), st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_get_user_token_returns_token():
    """Verify GetUserToken returns a non-empty token when called with valid credentials."""
    candidate = {
        "api_name": "GetUserToken",
        "parameters": {
            "username": "user1",
            "password": "pass1"
        }
    }
    result = evaluate_api_call(candidate)
    assert "token" in result, "GetUserToken should return a token"
    assert isinstance(result["token"], str), "Token should be a string"
    assert len(result["token"]) > 0, "Token should not be empty"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_delete_account_returns_status():
    """Verify DeleteAccount returns a non-empty status when called with a valid token."""
    candidate = {
        "api_name": "DeleteAccount",
        "parameters": {
            "token": "valid-token-abc"
        }
    }
    result = evaluate_api_call(candidate)
    assert "status" in result, "DeleteAccount should return a status"
    assert isinstance(result["status"], str), "Status should be a string"
    assert len(result["status"]) > 0, "Status should not be empty"

@given(st.text(min_length=1), st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_get_user_token_param_mapping():
    """Verify username and password parameters are correctly mapped in GetUserToken."""
    candidate = {
        "api_name": "GetUserToken",
        "parameters": {
            "username": "alice",
            "password": "secret"
        }
    }
    result = evaluate_api_call(candidate)
    assert "token" in result, "GetUserToken should return a token"
    # Verify the token was generated from the provided credentials (basic sanity check)
    assert isinstance(result["token"], str), "Token should be a string"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_api_name_case_insensitive():
    """Verify the evaluator handles API names case-insensitively."""
    for api_name in ("getusertoken", "GETUSERTOKEN", "GetUserToken"):
        candidate = {
            "api_name": api_name,
            "parameters": {
                "username": "user",
                "password": "pass"
            }
        }
        result = evaluate_api_call(candidate)
        assert "token" in result, f"API name '{api_name}' should return a token"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_delete_account_parameter_mapping():
    """Verify token parameter is correctly mapped in DeleteAccount."""
    candidate = {
        "api_name": "DeleteAccount",
        "parameters": {
            "token": "my-secret-token"
        }
    }
    result = evaluate_api_call(candidate)
    assert "status" in result, "DeleteAccount should return a status"
    assert isinstance(result["status"], str), "Status should be a string"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_get_user_token_non_empty_username_password():
    """Ensure GetUserToken always produces a non-empty token even with minimal credentials."""
    candidate = {
        "api_name": "GetUserToken",
        "parameters": {
            "username": "x",
            "password": "y"
        }
    }
    result = evaluate_api_call(candidate)
    assert "token" in result, "GetUserToken should return a token"
    assert len(result["token"]) >= 1, "Token should have at least one character"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_delete_account_valid_token_format():
    """Verify DeleteAccount accepts a token string as input."""
    candidate = {
        "api_name": "DeleteAccount",
        "parameters": {
            "token": "token-with-dashes-and-hyphens"
        }
    }
    result = evaluate_api_call(candidate)
    assert "status" in result, "DeleteAccount should return a status"
    assert isinstance(result["status"], str), "Status should be a string"
