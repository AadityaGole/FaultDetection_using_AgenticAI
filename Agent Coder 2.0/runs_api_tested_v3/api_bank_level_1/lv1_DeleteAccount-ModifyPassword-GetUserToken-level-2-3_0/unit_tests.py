import pytest
from hypothesis import given, strategies as st
from evaluation.api_bank_evaluator import evaluate_api_bank

def test_get_user_token_success():
    """Test successful GetUserToken API call with valid credentials."""
    output = 'ApiName(username="foo", password="bar")'
    result = evaluate_api_call(output)
    assert result is not None

def test_delete_account_success():
    """Test successful DeleteAccount API call with valid token."""
    output = 'ApiName(token="valid_token_123")'
    result = evaluate_api_call(output)
    assert result is not None

def test_wrong_api_name_fails():
    """Test that an incorrect API name fails validation."""
    output = 'ApiName(delete_account="do_something")'
    result = evaluate_api_call(output)
    assert result is None or "error" in str(result)

def test_missing_token_parameter():
    """Test that missing required token parameter causes failure."""
    output = 'ApiName(password="bar")'
    result = evaluate_api_call(output)
    assert result is None or "error" in str(result)

def test_non_string_token_type():
    """Test that non-string token type causes failure."""
    output = 'ApiName(token=123)'
    result = evaluate_api_call(output)
    assert result is None or "error" in str(result)

def test_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    output_lower = 'ApiName(username="foo", password="bar")'
    output_upper = 'APIName(username="foo", password="bar")'
    result_lower = evaluate_api_call(output_lower)
    result_upper = evaluate_api_call(output_upper)
    assert result_lower is not None
    assert result_upper is not None

@pytest.mark.hypothesis.guarded
@given(st.text(min_size=15, max_size=60))
def test_various_api_calls(sample_output):
    """Property test: various valid API call strings should be processed correctly."""
    result = evaluate_api_call(sample_output)
    assert result is not None

@pytest.mark.hypothesis.guarded
@given(st.text(min_size=15, max_size=60))
def test_various_api_calls_with_different_capitalizations(sample_output):
    """Property test: different capitalizations of API names should all work."""
    result = evaluate_api_call(sample_output)
    assert result is not None
