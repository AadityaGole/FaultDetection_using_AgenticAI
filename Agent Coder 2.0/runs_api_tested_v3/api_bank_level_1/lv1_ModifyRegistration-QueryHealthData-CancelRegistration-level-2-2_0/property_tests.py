from hypothesis import given, strategies as st, settings, assume

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.sampled_from(["2023-03-26", "2023-01-15", "2023-12-31", "2024-02-14"]),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_valid_parameters(appointment_id, new_appointment_date, new_appointment_doctor):
    """Test that valid parameters are accepted and processed correctly."""
    result = evaluate_api_call("ModifyRegistration", appointment_id=appointment_id, new_appointment_date=new_appointment_date, new_appointment_doctor=new_appointment_doctor)
    assert isinstance(result, str), f"Expected string result, got {type(result)}"
    assert "success" in result.lower(), "Status should indicate successful modification"

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_invalid_date_format():
    """Test that invalid date formats are rejected by the evaluator."""
    invalid_dates = [
        "20230326",
        "2023/03/26",
        "Mar 26 2023",
        "",
        "2023-13-01",
        "2023-00-01",
    ]
    for date in invalid_dates:
        with pytest.raises((ValueError, KeyError)):
            evaluate_api_call("ModifyRegistration", appointment_id="12345", new_appointment_date=date, new_appointment_doctor="Dr. Smith")

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_missing_required_parameters():
    """Test that omitting required parameters causes the evaluator to fail."""
    # Omitting new_appointment_doctor should cause a failure
    with pytest.raises((ValueError, KeyError, AttributeError)):
        evaluate_api_call("ModifyRegistration", appointment_id="12345", new_appointment_date="2023-03-26")

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.sampled_from(["2023-03-26"]),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_correct_date_and_doctor():
    """Test that a specific valid combination works as expected."""
    result = evaluate_api_call("ModifyRegistration", appointment_id="abc123", new_appointment_date="2023-03-26", new_appointment_doctor="Dr. Lee")
    assert isinstance(result, str)
    assert "success" in result.lower()

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.text(min_size=7, max_size=20),
    new_appointment_doctor=st.text(min_size=1, max_size=30)
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_case_insensitive_api_name():
    """Test that the API name is matched case-insensitively."""
    # The evaluator should treat "modify_registration" same as "ModifyRegistration"
    # We test both forms to ensure case insensitivity
    result_upper = evaluate_api_call("MODIFYREGISTRATION", appointment_id="abc123", new_appointment_date="2023-03-26", new_appointment_doctor="Dr. Lee")
    result_lower = evaluate_api_call("modify_registration", appointment_id="abc123", new_appointment_date="2023-03-26", new_appointment_doctor="Dr. Lee")
    assert result_upper == result_lower, "Case-insensitive API name handling should yield identical results"

import pytest
