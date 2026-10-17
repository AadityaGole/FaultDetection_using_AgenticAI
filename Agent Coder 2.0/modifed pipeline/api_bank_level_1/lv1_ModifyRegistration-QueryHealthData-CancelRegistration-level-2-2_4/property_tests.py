from hypothesis import given, strategies as st, settings, assume

from evaluate_api_call import evaluate_api_call


# Test 1: CancelRegistration with existing appointment should succeed
@given(
    appointment_id=st.text(min_size=1, max_size=50),
    # Assume the appointment exists per spec precondition
)
@settings(max_examples=10, deadline=1500)
def test_cancel_registration_success(appointment_id):
    """Test that CancelRegistration returns a successful cancellation when appointment exists."""
    result = evaluate_api_call(candidate={
        "appointment_id": appointment_id,
        "status": "cancelled"
    })
    # The result should indicate successful cancellation
    assert result.passed is True
    # The status field should reflect the cancellation outcome
    assert "status" in result
    assert result["status"] == "cancelled"


# Test 2: CancelRegistration with non-existent appointment should fail appropriately
@given(
    appointment_id=st.text(min_size=1, max_size=50)
)
@settings(max_examples=10, deadline=1500)
def test_cancel_registration_failure(appointment_id):
    """Test that CancelRegistration handles non-existent appointments gracefully."""
    result = evaluate_api_call(candidate={
        "appointment_id": appointment_id,
        "status": "cancelled"
    })
    # Should still return a result (possibly with failure status)
    assert result is not None
    assert "status" in result
    # Status should indicate failure (e.g., "not_found" or similar)
    assert result["status"] != "cancelled"


# Test 3: CancelRegistration preserves appointment_id parameter
@given(
    appointment_id=st.text(min_size=1, max_size=50)
)
@settings(max_examples=10, deadline=1500)
def test_cancel_registration_param_preservation(appointment_id):
    """Test that the appointment_id parameter is preserved through the operation."""
    result = evaluate_api_call(candidate={
        "appointment_id": appointment_id,
        "status": "cancelled"
    })
    # The result should contain the original appointment_id
    assert "appointment_id" in result
    assert result["appointment_id"] == appointment_id


# Test 4: CancelRegistration with minimal valid input
@given(
    appointment_id=st.text(min_size=1, max_size=10)
)
@settings(max_examples=5, deadline=1500)
def test_cancel_registration_minimal_input(appointment_id):
    """Test cancellation with very short appointment ID."""
    result = evaluate_api_call(candidate={
        "appointment_id": appointment_id,
        "status": "cancelled"
    })
    assert result.passed is True
    assert "status" in result
    assert result["status"] == "cancelled"


# Test 5: CancelRegistration with longer appointment ID
@given(
    appointment_id=st.text(min_size=20, max_size=60)
)
@settings(max_examples=5, deadline=1500)
def test_cancel_registration_long_id(appointment_id):
    """Test cancellation with a longer appointment ID string."""
    result = evaluate_api_call(candidate={
        "appointment_id": appointment_id,
        "status": "cancelled"
    })
    assert result.passed is True
    assert "status" in result
    assert result["status"] == "cancelled"


# Test 6: CancelRegistration with special characters in appointment_id
@given(
    appointment_id=st.text(min_size=1, max_size=50)
)
@settings(max_examples=5, deadline=1500)
def test_cancel_registration_special_chars(appointment_id):
    """Test cancellation with appointment IDs containing special characters."""
    result = evaluate_api_call(candidate={
        "appointment_id": appointment_id,
        "status": "cancelled"
    })
    assert result.passed is True
    assert "status" in result
    assert result["status"] == "cancelled"
