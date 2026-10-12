from hypothesis import given, strategies as st, settings, assume

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_valid_call(appointment_id, new_appointment_date, new_appointment_doctor):
    # The evaluator should parse the API name exactly as 'ModifyRegistration'
    # and require all three parameters
    result = evaluate_api_call("ModifyRegistration", appointment_id, new_appointment_date, new_appointment_doctor)

    # Verify the API name was matched exactly (case-sensitive)
    assert result == "success"

    # Verify all three required parameters were accepted
    assert "appointment_id" in result.lower()
    assert "new_appointment_date" in result.lower()
    assert "new_appointment_doctor" in result.lower()

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_invalid_api_name():
    # Wrong API name should not pass
    result = evaluate_api_call("InvalidAPI", appointment_id="123", new_appointment_date="2023-10-15", new_appointment_doctor="Dr. Smith")
    assert result != "success"

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_missing_parameter():
    # Missing parameters should not pass
    # We'll try calling with only two parameters (should fail)
    with pytest.raises(AssertionError):
        evaluate_api_call("ModifyRegistration", "123", "2023-10-15")

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_wrong_date_format():
    # Date not in YYYY-MM-DD format should fail
    result = evaluate_api_call("ModifyRegistration", "123", "2023/10/15", "Dr. Smith")
    assert result != "success"

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_empty_doctor():
    # Empty doctor name should fail
    result = evaluate_api_call("ModifyRegistration", "123", "2023-10-15", "")
    assert result != "success"

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_short_string_values():
    # Very short strings should still work (within reasonable bounds)
    result = evaluate_api_call("ModifyRegistration", "a", "2023-01-01", "b")
    assert result == "success"

# Additional property: date format validation through Hypothesis
@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.datetimes(dt_format='%Y-%m-%d').map(lambda d: d.strftime('%Y-%m-%d')),
    new_appointment_doctor=st.text(min_size=1, max_size=50),
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_date_is_yyyymmdd():
    result = evaluate_api_call("ModifyRegistration", "123", new_appointment_date, new_appointment_doctor)
    assert result == "success"
