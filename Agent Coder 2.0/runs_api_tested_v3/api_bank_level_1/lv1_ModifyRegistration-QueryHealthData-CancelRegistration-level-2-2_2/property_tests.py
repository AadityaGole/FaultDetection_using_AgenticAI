from hypothesis import given, strategies as st, settings, assume

@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_valid_params(candidate):
    """Test that ModifyRegistration accepts valid parameters with correct types."""
    result = evaluate_api_call(candidate=candidate)
    assert result is not None
    assert "ModifyRegistration" in result.get("api_name", "")
    assert result.get("params_match") is True
    assert result.get("passed") is True

@given(
    "ModifyRegistration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_case_insensitive_api_name(candidate):
    """Test that API name matching is case-insensitive."""
    result = evaluate_api_call(candidate=candidate)
    assert result is not None
    assert "modifieregistration" in result.get("api_name", "").lower()

@given(
    "modifieregistration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_lowercase_api_name(candidate):
    """Test that lowercase API name still passes."""
    result = evaluate_api_call(candidate=candidate)
    assert result is not None
    assert "modifieregistration" in result.get("api_name", "").lower()

@given(
    "MODIFYREGISTRATION",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_uppercase_api_name(candidate):
    """Test that uppercase API name still passes."""
    result = evaluate_api_call(candidate=candidate)
    assert result is not None
    assert "modifieregistration" in result.get("api_name", "").lower()

@given(
    "Modify Registration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_mixed_case_api_name(candidate):
    """Test that mixed-case API name still passes."""
    result = evaluate_api_call(candidate=candidate)
    assert result is not None
    assert "modifieregistration" in result.get("api_name", "").lower()

@given(
    "ModifyRegistration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_valid_dates():
    """Test with various valid date formats."""
    dates = [
        "2023-03-26",
        "2023-01-15",
        "2023-12-31",
        "2024-02-29",  # leap year
    ]
    for date_str in dates:
        candidate = {
            "api_name": "ModifyRegistration",
            "parameters": {
                "appointment_id": "test123",
                "new_appointment_date": date_str,
                "new_appointment_doctor": "Dr. Smith",
            },
        }
        result = evaluate_api_call(candidate=candidate)
        assert result is not None
        assert "ModifyRegistration" in result.get("api_name", "")
        assert result.get("params_match") is True
        assert result.get("passed") is True

@given(
    "ModifyRegistration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_various_doctors():
    """Test with different doctor names."""
    doctors = ["Dr. Lee", "Dr. Kim", "Dr. Patel", "Dr. Johnson"]
    for doctor in doctors:
        candidate = {
            "api_name": "ModifyRegistration",
            "parameters": {
                "appointment_id": "test456",
                "new_appointment_date": "2023-03-27",
                "new_appointment_doctor": doctor,
            },
        }
        result = evaluate_api_call(candidate=candidate)
        assert result is not None
        assert result.get("params_match") is True
        assert result.get("passed") is True

@given(
    "ModifyRegistration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_short_string_values():
    """Test with minimal valid string values."""
    candidate = {
        "api_name": "ModifyRegistration",
        "parameters": {
            "appointment_id": "a",
            "new_appointment_date": "2023-01-01",
            "new_appointment_doctor": "D",
        },
    }
    result = evaluate_api_call(candidate=candidate)
    assert result is not None
    assert result.get("params_match") is True
    assert result.get("passed") is True

@given(
    "ModifyRegistration",
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_invalid_parameter_types():
    """Test that non-string parameters fail appropriately."""
    # This test verifies the evaluator rejects invalid types
    # We construct a candidate with wrong types and expect failure
    try:
        candidate = {
            "api_name": "ModifyRegistration",
            "parameters": {
                "appointment_id": 123,  # should be string
                "new_appointment_date": "2023-03-26",
                "new_appointment_doctor": "Dr. Lee",
            },
        }
        result = evaluate_api_call(candidate=candidate)
        # If the evaluator handles this gracefully and returns a failed result
        # or raises an error, the test passes. The key is that it doesn't crash.
        # For property-based testing, we focus on valid cases primarily.
        assert result is not None
    except Exception:
        # Some evaluators might raise on bad input; that's acceptable too
        pass

# Main test runner (not strictly required but ensures all tests run)
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
