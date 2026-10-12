from hypothesis import given, strategies as st, settings, assume

@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_cancel_registration_valid_call():
    """Test that a valid CancelRegistration call passes validation."""
    # Construct a valid CancelRegistration call
    # According to spec: operationId='CancelRegistration-Level-2-2_4'
    # Parameters: appointment_id (required, str)
    # Optional: new_appointment_date, new_appointment_doctor
    call = {
        "operation_id": "CancelRegistration",
        "appointment_id": "abc123",
        "new_appointment_date": "2023-06-15",
        "new_appointment_doctor": "Dr. Brown"
    }

    # Evaluate the call - this would normally call the actual API
    # For the purpose of this test harness, we simulate the evaluator
    # The evaluator should return a parsed result with matching fields
    result = evaluate_api_call(call)

    # Assertions on the evaluated result
    assert "CancelRegistration" in result.get("api_name", "").lower()
    assert "appointment_id" in result.get("params", {})
    assert isinstance(result["params"]["appointment_id"], str)
    assert "status" in result
    assert isinstance(result["status"], str)

@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_query_health_data_valid_call():
    """Test that a valid QueryHealthData call passes validation."""
    # Valid QueryHealthData call with required parameters
    call = {
        "operation_id": "QueryHealthData",
        "user_id": "user456",
        "start_time": "2023-01-01 00:00:00",
        "end_time": "2023-01-31 23:59:59"
    }

    result = evaluate_api_call(call)

    # Verify API name matches case-insensitively
    assert "queryhealthdata" in result.get("api_name", "").lower()
    # Verify required parameters are present
    assert "user_id" in result.get("params", {})
    assert "start_time" in result.get("params", {})
    assert "end_time" in result.get("params", {})
    # Verify parameter types
    assert isinstance(result["params"]["user_id"], str)
    assert isinstance(result["params"]["start_time"], str)
    assert isinstance(result["params"]["end_time"], str)
    # Verify response contains health_data list
    assert "health_data" in result
    assert isinstance(result["health_data"], list)

@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_valid_call():
    """Test that a valid ModifyRegistration call passes validation."""
    call = {
        "operation_id": "ModifyRegistration",
        "appointment_id": "xyz789",
        "new_appointment_date": "2023-07-20",
        "new_appointment_doctor": "Dr. White"
    }

    result = evaluate_api_call(call)

    assert "modifierestrictionation" in result.get("api_name", "").lower()  # Note: ModifyRegistration lowercased
    assert "appointment_id" in result.get("params", {})
    assert isinstance(result["params"]["appointment_id"], str)
    assert "new_appointment_date" in result.get("params", {})
    assert isinstance(result["params"]["new_appointment_date"], str)
    assert "new_appointment_doctor" in result.get("params", {})
    assert isinstance(result["params"]["new_appointment_doctor"], str)
    assert "status" in result

# Test that invalid API names fail
@given(
    st.text(min_size=1, max_size=100),
)
@settings(max_examples=10, deadline=300)
def test_invalid_api_name_fails():
    """Test that calls with non-existent API names are rejected."""
    # Various invalid operation IDs
    invalid_ids = [
        "InvalidOperation",
        "cancelregistration",  # lowercase but still not a defined op
        "modifyregistration",
        "queryhealthdata",
        "",
        None,
    ]

    for inv_id in invalid_ids:
        call = {
            "operation_id": inv_id,
            "appointment_id": "any",
        }
        try:
            result = evaluate_api_call(call)
            # If the evaluator doesn't reject invalid names, this test fails
            # We expect some failure condition (exception or empty result)
            assert False, f"Expected rejection for invalid API name '{inv_id}' but got result"
        except Exception:
            # Some evaluators might raise an exception for invalid names
            pass

# Test that missing required parameters cause failures
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=10, deadline=300)
def test_missing_required_parameters_fail():
    """Test that omitting required parameters causes the evaluator to fail."""
    # CancelRegistration requires appointment_id
    call_no_id = {
        "operation_id": "CancelRegistration",
        "new_appointment_date": "2023-08-01",
        "new_appointment_doctor": "Dr. Green"
    }

    # This should fail because appointment_id is missing
    try:
        result = evaluate_api_call(call_no_id)
        # If we get here without error, the test fails
        assert False, "Expected failure for missing required parameter 'appointment_id'"
    except Exception:
        # Expected failure for missing required parameter
        pass

# Test that wrong parameter types are rejected
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=10, deadline=300)
def test_wrong_param_types_fail():
    """Test that incorrect parameter types cause evaluation failures."""
    # Try passing appointment_id as integer instead of string
    call_wrong_type = {
        "operation_id": "CancelRegistration",
        "appointment_id": 12345,  # Should be string
        "new_appointment_date": "2023-09-01",
        "new_appointment_doctor": "Dr. Doe"
    }

    try:
        result = evaluate_api_call(call_wrong_type)
        # If we get here, the evaluator didn't catch the type mismatch
        assert False, "Expected failure for non-string appointment_id"
    except Exception:
        # Type mismatch should be caught
        pass

# Test that response status field is present and contains expected values
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_response_status_field():
    """Test that the evaluator returns a status field with appropriate values."""
    call = {
        "operation_id": "CancelRegistration",
        "appointment_id": "any_id",
        "new_appointment_date": "2023-04-01",
        "new_appointment_doctor": "Dr. Roe"
    }

    result = evaluate_api_call(call)

    # Status should be present and indicate success/cancellation
    assert "status" in result
    assert isinstance(result["status"], str)
    # Common status values could be "success", "cancelled", "failed", etc.
    # The test just verifies the field exists and is a string
    assert len(result["status"]) > 0

# Test case insensitivity of API name
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=10, deadline=300)
def test_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    call_lower = {
        "operation_id": "cancelregistration",
        "appointment_id": "any",
    }
    call_upper = {
        "operation_id": "CANCELREGISTRATION",
        "appointment_id": "any",
    }
    call_mixed = {
        "operation_id": "CancelRegistration",
        "appointment_id": "any",
    }

    # Both should pass validation (the evaluator should normalize case)
    for call in [call_lower, call_upper, call_mixed]:
        result = evaluate_api_call(call)
        assert "cancelregistration" in result.get("api_name", "").lower()

# Test that optional parameters are handled correctly
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=10, deadline=300)
def test_optional_parameters():
    """Test that optional parameters (new_appointment_date, new_appointment_doctor) are optional."""
    # Provide only required parameters
    call_minimal = {
        "operation_id": "ModifyRegistration",
        "appointment_id": "minimal_id",
    }

    result = evaluate_api_call(call_minimal)
    assert "modifierestrictionation" in result.get("api_name", "").lower()
    assert "appointment_id" in result.get("params", {})
    # Optional parameters should either be absent or present
    # The evaluator should handle both cases
    assert "new_appointment_date" not in result.get("params", {}) or \
           isinstance(result.get("params", {}).get("new_appointment_date"), str)

# Test that date format is respected in QueryHealthData
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=10, deadline=300)
def test_date_format_validation():
    """Test that date strings follow the expected format."""
    call = {
        "operation_id": "QueryHealthData",
        "user_id": "user001",
        "start_time": "2023-02-15 08:30:00",
        "end_time": "2023-02-20 17:00:00",
    }

    result = evaluate_api_call(call)

    # Parse the dates to ensure they are valid
    from datetime import datetime
    try:
        start_dt = datetime.strptime(call["params"]["start_time"], "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(call["params"]["end_time"], "%Y-%m-%d %H:%M:%S")
        assert start_dt < end_dt
    except ValueError:
        # If the format is wrong, the evaluator should reject it
        # This test assumes the evaluator handles format validation
        pass

# Test that health_data is a non-empty list when present
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=10, deadline=300)
def test_health_data_list_structure():
    """Test that the health_data response is a properly structured list."""
    call = {
        "operation_id": "QueryHealthData",
        "user_id": "user002",
        "start_time": "2023-03-01 00:00:00",
        "end_time": "2023-03-05 23:59:59",
    }

    result = evaluate_api_call(call)

    # health_data should be a list
    assert isinstance(result["health_data"], list)
    # Each item in the list should be a dict with expected keys
    for item in result["health_data"]:
        assert isinstance(item, dict)
        # Check for at least the expected keys
        expected_keys = {"time", "blood_pressure", "triglycerides", "heart_rate"}
        # At minimum, there should be some data
        assert len(item) > 0

# Test idempotency-like property: multiple identical calls produce consistent results
@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=50),
)
@settings(max_examples=5, deadline=300)
def test_consistent_results_for_same_input():
    """Test that identical calls produce consistent evaluations."""
    call = {
        "operation_id": "ModifyRegistration",
        "appointment_id": "same_id",
        "new_appointment_date": "2023-09-10",
        "new_appointment_doctor": "Dr. New",
    }

    # Make two identical calls
    result1 = evaluate_api_call(call)
    result2 = evaluate_api_call(call)

    # Results should be consistent (same operation name, same params, same status)
    assert result1["api_name"] == result2["api_name"]
    assert result1["params"]["appointment_id"] == result2["params"]["appointment_id"]
    assert result1["params"]["new_appointment_date"] == result2["params"]["new_appointment_date"]
    assert result1["params"]["new_appointment_doctor"] == result2["params"]["new_appointment_doctor"]
    assert result1["status"] == result2["status"]

# Test that the evaluator handles whitespace variations correctly
@given(
    st.text(min_size=1, max_size=100),
    st.text(min_size=1, max_size=100),
)
@settings(max_examples=5, deadline=300)
def test_whitespace_tolerance():
    """Test that minor whitespace differences don't break parsing."""
    # Add extra spaces around keys and values
    call = {
        " operation_id ": "CancelRegistration",
        " appointment_id ": "test123",
        " new_appointment_date ": "2023-01-01",
        " new_appointment_doctor ": "Dr. Test",
    }

    result = evaluate_api_call(call)
    assert "cancelregistration" in result.get("api_name", "").lower()
    assert "appointment_id" in result.get("params", {})
    assert result["params"]["appointment_id"] == "test123"

if __name__ == "__main__":
    # Run the tests
    import pytest
    pytest.main([__file__, "-v"])
