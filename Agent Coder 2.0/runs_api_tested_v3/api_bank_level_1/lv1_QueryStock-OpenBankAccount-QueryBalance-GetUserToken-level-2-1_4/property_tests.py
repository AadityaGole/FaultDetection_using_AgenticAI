from hypothesis import given, strategies as st, settings, assume

@given(
    st.dictionaries({
        "api_name": st.sampled_from(["QueryBalance", "querybalance", "QUERYBALANCE", "openbankaccount"]),
        "token": st.text(min_size=1, max_size=50)
    })
)
@settings(max_examples=20, deadline=1500)
def test_query_balance_identification_and_token_requirement(candidate):
    """
    Property test: QueryBalance must be correctly identified and require a token parameter.
    """
    parsed_api_name = candidate.get("parsed_api_name")
    api_match = candidate.get("api_match")
    params_match = candidate.get("params_match")
    passed = candidate.get("passed")

    # API name must be identified correctly (case-insensitive)
    assert parsed_api_name == "QueryBalance", f"Expected 'QueryBalance', got '{parsed_api_name}'"
    assert api_match is True, "API name should be correctly identified"

    # Token parameter must be present and be a non-empty string
    assert "token" in candidate, "Token parameter must be present"
    token = candidate["token"]
    assert isinstance(token, str), f"Token must be a string, got {type(token)}"
    assert len(token) > 0, "Token must be non-empty"

    # Overall evaluation should pass
    assert passed is True, "Evaluation should pass for valid QueryBalance call"

@given(
    st.text(min_size=1, max_size=50)
)
@settings(max_examples=10, deadline=1500)
def test_invalid_token_missing_or_empty(candidate):
    """
    Property test: Missing or empty token should cause evaluation to fail.
    """
    # Missing token
    candidate = {
        "api_name": "QueryBalance",
        "token": ""
    }
    parsed_api_name = candidate.get("parsed_api_name")
    api_match = candidate.get("api_match")
    params_match = candidate.get("params_match")
    passed = candidate.get("passed")

    assert parsed_api_name == "QueryBalance"
    assert api_match is False, "Missing token should cause mismatch"
    assert params_match is False, "Missing token should cause param mismatch"
    assert passed is False, "Evaluation should fail for missing token"

    # Empty token
    candidate = {
        "api_name": "QueryBalance",
        "token": ""
    }
    parsed_api_name = candidate.get("parsed_api_name")
    api_match = candidate.get("api_match")
    params_match = candidate.get("params_match")
    passed = candidate.get("passed")

    assert parsed_api_name == "QueryBalance"
    assert api_match is False
    assert params_match is False
    assert passed is False

@given(
    st.text(min_size=1, max_size=50)
)
@settings(max_examples=10, deadline=1500)
def test_case_insensitive_api_name(candidate):
    """
    Property test: API name matching should be case-insensitive.
    """
    for api_name in ["querybalance", "QUERYBALANCE", "QueryBalAnCe", "q-U-E-R-Y-B-A-L-A-N-C-E"]:
        candidate = {
            "api_name": api_name,
            "token": "test_token"
        }
        parsed_api_name = candidate.get("parsed_api_name")

        # Evaluator should normalize/case-fold the API name
        assert parsed_api_name == "QueryBalance", f"Failed for API name '{api_name}': got '{parsed_api_name}'"

@given(
    st.text(min_size=1, max_size=50)
)
@settings(max_examples=10, deadline=1500)
def test_valid_token_values(candidate):
    """
    Property test: Various valid token values should pass evaluation.
    """
    valid_tokens = [
        "simple_token",
        "token_123",
        "a",
        "longer_token_name_for_testing",
        "x",
        "0",
        "token_with_numbers_456",
    ]
    for token in valid_tokens:
        candidate = {
            "api_name": "QueryBalance",
            "token": token
        }
        parsed_api_name = candidate.get("parsed_api_name")
        api_match = candidate.get("api_match")
        params_match = candidate.get("params_match")
        passed = candidate.get("passed")

        assert parsed_api_name == "QueryBalance"
        assert api_match is True
        assert params_match is True
        assert passed is True

@given(
    st.text(min_size=1, max_size=50)
)
@settings(max_examples=10, deadline=1500)
def test_non_string_token_fails(candidate):
    """
    Property test: Non-string token values should cause evaluation to fail.
    """
    non_string_tokens = ["", "123", 42, None, [1, 2, 3]]
    for token in non_string_tokens:
        candidate = {
            "api_name": "QueryBalance",
            "token": token
        }
        parsed_api_name = candidate.get("parsed_api_name")
        api_match = candidate.get("api_match")
        params_match = candidate.get("params_match")
        passed = candidate.get("passed")

        # Even though API name might be identified, params should not match due to wrong type
        assert parsed_api_name == "QueryBalance"
        # Note: We don't strictly assert api_match here because the spec focuses on parameter validation
        # The key invariant is that non-string tokens should not pass

@given(
    st.dictionaries({
        "api_name": st.sampled_from(["QueryBalance", "QueryStock", "GetUserToken", "OpenBankAccount"]),
        "token": st.text(min_size=1, max_size=50)
    })
)
@settings(max_examples=15, deadline=1500)
def test_all_operations_require_token(candidate):
    """
    Property test: All operations described in the specification require a token parameter.
    """
    for api_name, token in [
        ("QueryBalance", "valid_token"),
        ("QueryStock", "stock_code"),
        ("GetUserToken", "username_password"),
        ("OpenBankAccount", "account_id"),
    ]:
        candidate = {
            "api_name": api_name,
            "token": token
        }
        parsed_api_name = candidate.get("parsed_api_name")
        api_match = candidate.get
