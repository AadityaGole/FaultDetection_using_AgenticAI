from hypothesis import given, strategies as st, settings, assume

@given(st.text(min_length=1), st.text(min_length=1), st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_cancel_registration_makes_appointment_cancelled(appointment_id, old_date, old_doctor):
    """
    Test that CancelRegistration marks the appointment as cancelled.
    Verifies the postcondition that the appointment is in a cancelled state.
    """
    result = api_call("CancelRegistration", {"appointment_id": appointment_id})
    # The result should indicate the cancellation was successful and the appointment is now cancelled
    assert "cancelled" in result.lower(), f"Expected cancelled status in result: {result}"

@given(st.text(min_length=1), st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_cancel_already_cancelled(appointment_id):
    """
    Test that cancelling an already cancelled appointment is handled correctly.
    Verifies the invariant that a cancelled appointment remains in a cancelled state.
    """
    # First cancel the appointment
    api_call("CancelRegistration", {"appointment_id": appointment_id})

    # Try to cancel again - should not change state (remains cancelled)
    result = api_call("CancelRegistration", {"appointment_id": appointment_id})
    assert "cancelled" in result.lower(), f"After re-cancellation, expected cancelled status: {result}"

@given(st.text(min_length=1), st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_cannot_modify_after_cancellation(appointment_id):
    """
    Test that an appointment cannot be modified after it has been cancelled.
    Verifies the invariant that cancelled appointments cannot be modified.
    """
    # First cancel the appointment
    api_call("CancelRegistration", {"appointment_id": appointment_id})

    # Attempt to modify - should leave the appointment in cancelled state
    result = api_call("ModifyRegistration", {
        "appointment_id": appointment_id,
        "new_appointment_date": "2023-04-01",
        "new_appointment_doctor": "Dr. Brown"
    })
    # The result should indicate failure or unchanged state (still cancelled)
    assert "cancelled" in result.lower(), f"After cancellation, expected cancelled status during modification: {result}"

@given(st.text(min_length=1), st.text(min_length=1), st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_cancel_with_valid_parameters(appointment_id, new_date, new_doctor):
    """
    Test that CancelRegistration with valid parameters produces the expected result.
    Verifies basic functionality with different inputs.
    """
    result = api_call("CancelRegistration", {
        "appointment_id": appointment_id,
        "new_appointment_date": new_date,
        "new_appointment_doctor": new_doctor
    })
    # The result should indicate success
    assert "success" in result.lower(), f"Expected success status: {result}"
