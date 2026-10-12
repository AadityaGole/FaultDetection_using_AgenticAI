from hypothesis import given, strategies as st, settings, assume

# Strategy for valid account, password, name parameters (non-empty strings)
valid_params = st.text(min_size=1, max_size=50)

@given(
    account=valid_params,
    password=valid_params,
    name=valid_params,
    api_name="OpenBankAccount"
)
@settings(max_examples=20, deadline=1500)
def test_openbankaccount_valid_params(api_name, account, password, name):
    """Test that valid API calls with all required string parameters parse correctly."""
    # Construct the API call dictionary
    candidate = {
        "api_name": api_name,
        "account": account,
        "password": password,
        "name": name
    }

    # Evaluate the API call through the entry point
    result = evaluate_api_call(candidate)

    # Assert the parsed API name matches the expected case-insensitive identity
    assert result["parsed_api_name"] == "OpenBankAccount"
    # Assert the API name match flag is True
    assert result["api_match"] is True
    # Assert the parameters were correctly extracted and match
    assert result["params_match"] is True
    # Assert the evaluation passed (successful account creation)
    assert result["passed"] is True

@given(
    account=valid_params,
    password=valid_params,
    name=valid_params,
    api_name="openbankaccount"
)
@settings(max_examples=20, deadline=1500)
def test_case_insensitive_api_name(api_name, account, password, name):
    """Test that the API name is case-insensitive during parsing."""
    candidate = {
        "api_name": api_name,
        "account": account,
        "password": password,
        "name": name
    }

    result = evaluate_api_call(candidate)

    # The parser should treat different cases as the same API
    assert result["parsed_api_name"] == "OpenBankAccount"
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

@given(
    account=valid_params,
    password=valid_params,
    name=valid_params,
    api_name="OPENBANKACCOUNT"
)
@settings(max_examples=20, deadline=1500)
def test_uppercase_api_name(api_name, account, password, name):
    """Test uppercase API name variant."""
    candidate = {
        "api_name": api_name,
        "account": account,
        "password": password,
        "name": name
    }

    result = evaluate_api_call(candidate)

    assert result["parsed_api_name"] == "OpenBankAccount"
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

@given(
    account=valid_params,
    password=valid_params,
    name=valid_params,
    api_name="OpenBankAccount"
)
@settings(max_examples=20, deadline=1500)
def test_malformed_call_missing_account(api_name, account, password, name):
    """Test that missing required parameters cause failure."""
    # Intentionally omit the account field
    candidate = {
        "api_name": api_name,
        "password": password,
        "name": name
    }

    result = evaluate_api_call(candidate)

    # Should fail due to missing required parameter
    assert result["passed"] is False
    # API name should still be identified but parameters won't match
    assert result["parsed_api_name"] == "OpenBankAccount"

@given(
    account=valid_params,
    password=valid_params,
    name=valid_params,
    api_name="OpenBankAccount"
)
@settings(max_examples=20, deadline=1500)
def test_malformed_call_wrong_type():
    """Test that non-string parameters cause failure."""
    # Pass integer instead of string for account
    candidate = {
        "api_name": "OpenBankAccount",
        "account": 12345,  # Not a string
        "password": "pass",
        "name": "John"
    }

    result = evaluate_api_call(candidate)

    # Should fail because account is not a string
    assert result["passed"] is False

@given(
    account=valid_params,
    password=valid_params,
    name=valid_params,
    api_name="OpenBankAccount"
)
@settings(max_examples=20, deadline=1500)
def test_empty_string_parameters():
    """Test that empty string parameters are rejected."""
    candidate = {
        "api_name": "OpenBankAccount",
        "account": "",
        "password": "",
        "name": ""
    }

    result = evaluate_api_call(candidate)

    # Should fail because parameters must be non-empty strings
    assert result["passed"] is False

@given(
    account=st.text(min_size=1),
    password=st.text(min_size=1),
    name=st.text(min_size=1),
    api_name="OpenBankAccount"
)
@settings(max_examples=15, deadline=1200)
def test_minimum_length_parameters():
    """Test that minimal non-empty strings satisfy the constraint."""
    candidate = {
        "api_name": "OpenBankAccount",
        "account": "a",
        "password": "p",
        "name": "n"
    }

    result = evaluate_api_call(candidate)

    # Should succeed with minimal valid inputs
    assert result["passed"] is True
    assert result["parsed_api_name"] == "OpenBankAccount"
    assert result["api_match"] is True
    assert result["params_match"] is True
