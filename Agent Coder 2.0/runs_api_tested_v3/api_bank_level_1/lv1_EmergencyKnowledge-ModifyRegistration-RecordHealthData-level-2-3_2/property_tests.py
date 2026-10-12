from hypothesis import given, strategies as st, settings, assume

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_valid_call(appointment_id, new_appointment_date, new_appointment_doctor):
    """Test that a valid ModifyRegistration call with all required parameters passes validation."""
    candidate = {
        "operationId": "OP-lv1_EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3_2",
        "operationName": "ModifyRegistration",
        "parameters": {
            "appointment_id": appointment_id,
            "new_appointment_date": new_appointment_date,
            "new_appointment_doctor": new_appointment_doctor
        }
    }
    result = evaluate_api_call(candidate)

    # Verify API name matches exactly
    assert result.get("api_name") == "ModifyRegistration"

    # Verify all required parameters are present
    assert "appointment_id" in result.get("params", {})
    assert "new_appointment_date" in result.get("params", {})
    assert "new_appointment_doctor" in result.get("params", {})

    # Verify parameter types
    assert isinstance(result["params"]["appointment_id"], str)
    assert isinstance(result["params"]["new_appointment_date"], str)
    assert isinstance(result["params"]["new_appointment_doctor"], str)

    # Verify specific values for the known scenario
    assert result["params"]["appointment_id"] == "90123456"
    assert result["params"]["new_appointment_date"] == "2023-10-15"
    assert result["params"]["new_appointment_doctor"] == "Dr. Johnson"

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_wrong_api_name():
    """Test that a call with wrong API name fails validation."""
    candidate = {
        "operationId": "OP-lv1_EmergencyKnowledge-WrongName",
        "operationName": "WrongOperation",
        "parameters": {
            "appointment_id": "90123456",
            "new_appointment_date": "2023-10-15",
            "new_appointment_doctor": "Dr. Johnson"
        }
    }
    result = evaluate_api_call(candidate)
    # Should not match ModifyRegistration
    assert result.get("api_name") != "ModifyRegistration"

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_missing_required_parameters():
    """Test that missing required parameters causes failure."""
    # Missing new_appointment_date
    candidate = {
        "operationId": "OP-lv1_EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3_2",
        "operationName": "ModifyRegistration",
        "parameters": {
            "appointment_id": "90123456",
            "new_appointment_doctor": "Dr. Johnson"
        }
    }
    result = evaluate_api_call(candidate)
    # Should not match due to missing required parameter
    assert result.get("api_match") is False or result.get("params_match") is False

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_invalid_date_format():
    """Test that invalid date format causes failure."""
    candidate = {
        "operationId": "OP-lv1_EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3_2",
        "operationName": "ModifyRegistration",
        "parameters": {
            "appointment_id": "90123456",
            "new_appointment_date": "2023-13-01",  # Invalid month
            "new_appointment_doctor": "Dr. Johnson"
        }
    }
    result = evaluate_api_call(candidate)
    # Should fail validation due to invalid date
    assert result.get("api_match") is False or result.get("params_match") is False

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_empty_doctor():
    """Test that empty doctor name causes failure."""
    candidate = {
        "operationId": "OP-lv1_EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3_2",
        "operationName": "ModifyRegistration",
        "parameters": {
            "appointment_id": "90123456",
            "new_appointment_date": "2023-10-15",
            "new_appointment_doctor": ""  # Empty string
        }
    }
    result = evaluate_api_call(candidate)
    # Should fail due to empty doctor name
    assert result.get("api_match") is False or result.get("params_match") is False

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_different_api_name():
    """Test that a different API name variant still works if it maps correctly."""
    candidate = {
        "operationId": "OP-lv1_EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3_2",
        "operationName": "ModifyRegistration",
        "parameters": {
            "appointment_id": "90123456",
            "new_appointment_date": "2023-10-15",
            "new_appointment_doctor": "Dr. Johnson"
        }
    }
    result = evaluate_api_call(candidate)
    # This should pass since the name is correct
    assert result.get("api_name") == "ModifyRegistration"
    assert result.get("params")["appointment_id"] == "90123456"
    assert result.get("params")["new_appointment_date"] == "2023-10-15"
    assert result.get("params
