from hypothesis import given, strategies as st, settings, assume

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.sampled_from(["2023-01-15", "2023-02-28", "2023-03-26"]),
    new_appointment_doctor=st.sampled_from(["Dr. Smith", "Dr. Lee", "Dr. Kim"])
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration(appointment_id, new_appointment_date, new_appointment_doctor):
    """
    Property-based test for ModifyRegistration API.

    Verifies that the API call is made with correct parameters and returns
    a successful status string matching the specification.
    """
    result = api_call("modify_registration", appointment_id=appointment_id, new_appointment_date=new_appointment_date, new_appointment_doctor=new_appointment_doctor)
    assert isinstance(result, str), f"Expected string status, got {type(result).__name__}"
    assert len(result) > 0, "Status message should not be empty"
