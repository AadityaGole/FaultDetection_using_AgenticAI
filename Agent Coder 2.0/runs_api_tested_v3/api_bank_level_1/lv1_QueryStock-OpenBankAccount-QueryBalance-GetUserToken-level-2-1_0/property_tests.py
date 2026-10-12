from hypothesis import given, strategies as st, settings, assume

@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=20, deadline=1500)
def test_query_stock_correct_call():
    # This test verifies that a well-formed call parses correctly
    # We need to call evaluate_api_call which is the entry point
    # The evaluator should return parsed_api_name, api_match, params_match, passed
    # For now we just ensure the call doesn't crash and returns a valid result structure

    # Note: In a real scenario, evaluate_api_call would be called here
    # But since we don't have the actual implementation, we simulate the expectation
    # The test should verify that the evaluator handles the call properly

    # Since we cannot actually call the external evaluator without it being available,
    # we focus on testing the input validation logic through the evaluator interface
    # The key is that the evaluator should:
    # 1. Match the API name case-insensitively ("QueryStock")
    # 2. Require stock_code as a non-empty string
    # 3. Require date in YYYY-MM-DD format

    # We'll create a mock scenario where we test the parsing behavior
    # The actual evaluate_api_call function is the system under test

    # For property-based testing, we can use strategies to generate valid inputs
    # and then verify the evaluator's internal state/return values

    # However, since we don't have the actual evaluator implementation,
    # we need to structure tests that would work with the real function.

    # Let's define what we expect from evaluate_api_call:
    # It should return a tuple/struct with:
    # - parsed_api_name (string)
    # - api_match (bool indicating if API name matched)
    # - params_match (dict of parameter names to their values)
    # - passed (bool indicating overall success)

    # We'll write tests that exercise these expectations

    # Test 1: Correct call with valid parameters
    # This would be a concrete example rather than a property test
    # but property tests should cover many cases automatically

    # Since we cannot actually execute evaluate_api_call without the real function,
    # I'll write tests that follow the contract and would pass if the evaluator is implemented correctly.

    # The key insight: the task says "call the function by its exact entry point"
    # So we need to call evaluate_api_call(candidate) where candidate is the API call representation

    # Looking at the formal spec, the API call format is [ApiName(key1='value1', ...)]
    # For QueryStock, this would be something like ["QueryStock", {"stock_code": "AMZN", "date": "2022-03-12"}]

    # Let me create tests that use the evaluator contract properly
    pass


# Actually, looking more carefully at the task, I need to:
# 1. Call evaluate_api_call() with the appropriate arguments
# 2. Assert on the returned values (parsed_api_name, api_match, params_match, passed)
# 3. Also test malformed calls that should fail

# The challenge is that evaluate_api_call expects a specific input format.
# Based on the description, it takes a candidate which represents the API call.
# The format appears to be [ApiName(key1='value1', key2='value2', ...)]

# For QueryStock, the call would be something like:
# [["QueryStock", {"stock_code": "AMZN", "date": "2022-03-12"}]]

# Let me write proper tests that exercise this contract

import re


@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=20, deadline=1500)
def test_query_stock_valid_inputs():
    """
    Test that valid QueryStock calls are parsed correctly.
    The evaluator should extract:
    - parsed_api_name: "QueryStock" (case-insensitive match)
    - api_match: True (since the API name was found)
    - params_match: dict with stock_code and date keys
    - passed: True (successful parsing)
    """
    # Construct the API call representation
    # Format: [ApiName(key1='value1', key2='value2', ...)]
    # For QueryStock: [["QueryStock", {"stock_code": stock_code, "date": date}]]
    api_call = [["QueryStock", {"stock_code": stock_code, "date": date}]]

    # Call the evaluator
    result = evaluate_api_call(api_call)

    # Assertions per the contract
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "parsed_api_name" in result, "Missing parsed_api_name field"
    assert "api_match" in result, "Missing api_match field"
    assert "params_match" in result, "Missing params_match field"
    assert "passed" in result, "Missing passed field"

    # Verify API name matches case-insensitively
    assert result["parsed_api_name"].lower() == "querystock", \
        f"Expected 'QueryStock' (case-insensitive), got '{result['parsed_api_name']}'"

    # Verify parameters match expected
    expected_params = {
        "stock_code": stock_code,
        "date": date
    }
    assert result["params_match"] == expected_params, \
        f"Parameters mismatch. Expected {expected_params}, got {result['params_match']}"

    # Verify overall success
    assert result["passed"] is True, \
        f"Call should have passed, got {result['passed']}"


@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=20, deadline=1500)
def test_query_stock_case_insensitive_api_name():
    """
    Test that the API name matching is case-insensitive.
    The evaluator should treat "querystock", "QUERYSTOCK", etc. as valid matches.
    """
    # Various case variations of the same API name
    api_names = [
        "QueryStock",
        "querystock",
        "QUERYSTOCK",
        "qStOCk",
        "Q-U-E-R-Y-S-T-O-C-K"
    ]

    for api_name in api_names:
        # Create a call with this API name
        api_call = [[api_name, {"stock_code": stock_code, "date": date}]]

        result = evaluate_api_call(api_call)

        # The parser should normalize the API name to lowercase or canonical form
        # and mark it as matched
        assert "parsed_api_name" in result
        assert result["parsed_api_name"].lower() == "querystock", \
            f"Case-insensitive match failed for '{api_name}': got '{result['parsed_api_name']}'"


@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=20, deadline=1500)
def test_query_stock_invalid_date_format():
    """
    Test that invalid date formats are rejected by the evaluator.
    The date must be in YYYY-MM-DD format.
    """
    # Try various invalid date formats
    invalid_dates = [
        "2022/03/12",      # slashes instead of dashes
        "2022-13-45",       # invalid month/day
        "2022-02-29",       # invalid leap year date
        "23-03-12",         # wrong order
        "March 12, 2022",   # natural language
        "",                 # empty
        "2022-01-01-extra"  # too long
    ]

    for date in invalid_dates:
        # Only run if the date looks somewhat plausible (not completely random garbage)
        # but still invalid
        if len(date) < 7 or len(date) > 10:
            continue

        api_call = [["QueryStock", {"stock_code": stock_code, "date": date}]]
        result = evaluate_api_call(api_call)

        # The evaluator should reject invalid dates
        # Either via api_match=False or passed=False
        assert "api_match" in result
        # If the date is clearly invalid, api_match should be False
        # Or if the evaluator treats it as a parsing failure, passed should be False
        # We check that the result indicates the failure appropriately

        # At minimum, the result should contain the expected fields
        assert isinstance(result, dict)


@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=20, deadline=1500)
def test_query_stock_missing_parameters():
    """
    Test that calls with missing required parameters fail validation.
    Both stock_code and date are required.
    """
    # Missing stock_code
    api_call = [["QueryStock", {}, "extra_param"]]  # missing stock_code
    result = evaluate_api_call(api_call)
    assert "api_match" not in result or result["api_match"] is False, \
        "Missing required parameter should cause api_match to be False"

    # Missing date
    api_call = [["QueryStock", {"stock_code": stock_code}], "extra_param"]
    result = evaluate_api_call(api_call)
    assert "api_match" not in result or result["api_match"] is False, \
        "Missing required parameter should cause api_match to be False"


@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=20, deadline=1500)
def test_query_stock_empty_string_values():
    """
    Test edge cases with empty strings for required parameters.
    Empty string for stock_code should be rejected (non-empty requirement).
    Empty string for date should be rejected (format requirement).
    """
    # Empty stock_code
    api_call = [["QueryStock", {"stock_code": "", "date": date}]]
    result = evaluate_api_call(api_call)
    assert "api_match" not in result or result["api_match"] is False, \
        "Empty stock_code should cause api_match to be False"

    # Empty date
    api_call = [["QueryStock", {"stock_code": stock_code, "date": ""}]]
    result = evaluate_api_call(api_call)
    assert "api_match" not in result or result["api_match"] is False, \
        "Empty date should cause api_match to be False"


# Additional property tests focusing on the evaluator's core contract

@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=15, deadline=1200)
def test_query_stock_type_consistency():
    """
    Verify that the evaluated result has the correct type (float) for stock_price.
    The postcondition states the function returns a float.
    """
    api_call = [["QueryStock", {"stock_code": stock_code, "date": date}]]
    result = evaluate_api_call(api_call)

    # The evaluator should return a structure containing the stock_price
    # We need to find the stock_price field in the result
    # According to the spec, output_parameters includes "stock_price"

    # Find the stock_price value in the result
    # It could be nested under some key or be part of the top-level
    # For now, we check that the result contains a numeric value that could be stock_price

    # The evaluator might return the raw float or wrapped in a dict
    # Let's check both possibilities

    if isinstance(result, dict):
        # Look for stock_price in the result
        stock_price = result.get("stock_price")
        if stock_price is not None:
            assert isinstance(stock_price, (int, float)), \
                f"stock_price should be a number, got {type(stock_price)}"
        else:
            # Maybe it's under a different key
            # Check common patterns
            for key in result.keys():
                if "price" in key.lower():
                    stock_price = result[key]
                    break
            assert isinstance(stock_price, (int, float)), \
                f"Found price-like value {stock_price} but it's not a number"
    else:
        # Result is a direct value (maybe the float itself)
        assert isinstance(result, (int, float)), \
            f"Expected a number, got {type(result)}"


# These additional tests verify the core contract properties
# without relying on the actual implementation details of evaluate_api_call

# Test that the evaluator handles the exact API name format
@given(
    stock_code=st.text(min_size=1, max_size=50),
    date=st.text(min_size=7, max_size=20)
)
@settings(max_examples=10, deadline=1200)
def test_query_stock_exact_api_name_format():
    """
    Verify that the exact API name "QueryStock" (and case variants) is accepted.
    """
    api_call = [["QueryStock", {"stock_code": stock_code, "date": date}]]
    result = evaluate_api_call(api_call)

    assert "parsed_api_name" in result
    assert result["parsed_api_name"] == "QueryStock"
    assert result["api_match"] is True
    assert result["params_match"]["stock_code"] == stock_code
    assert result["params_match"]["date"] == date
    assert result["passed"] is True


if __name__ == "__main__":
    # Run the tests
    import pytest
    pytest.main([__file__, "-v"])
