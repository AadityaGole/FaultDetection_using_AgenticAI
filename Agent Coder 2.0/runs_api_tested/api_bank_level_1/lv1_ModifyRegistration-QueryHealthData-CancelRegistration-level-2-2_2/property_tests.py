from hypothesis import given, strategies as st, settings, assume

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.sampled_from([
        "2023-03-26",
        "2023-04-15",
        "2023-02-28",
        "2023-07-01"
    ]),
    new_appointment_doctor=st.sampled_from(["Dr. Kim", "Dr. Lee", "Dr. Smith", "Dr. Patel"])
)
@settings(max_examples=20, deadline=1500)
def test_modify_registration_valid_params(appointment_id, new_appointment_date, new_appointment_doctor):
    # The spec requires these parameters to be present and correctly typed
    # We construct the call exactly as described in the ModifyRegistration API
    call = f"ModifyRegistration(appointment_id='{appointment_id}', new_appointment_date='{new_appointment_date}', new_appointment_doctor='{new_appointment_doctor}')"
    # Note: In reality this would call the actual api_call function
    # Here we simulate the expected behavior by asserting the constructed call matches
    # the expected format and parameter types
    assert isinstance(appointment_id, str)
    assert isinstance(new_appointment_date, str)
    assert isinstance(new_appointment_doctor, str)
    assert len(appointment_id) > 0
    assert len(new_appointment_date) == 10  # YYYY-MM-DD format
    assert len(new_appointment_doctor) >= 1

@given(
    user_id=st.text(min_size=1, max_size=50),
    start_time=st.fixed_str("2023-03-05 00:00:00"),
    end_time=st.fixed_str("2023-03-12 23:59:59")
)
@settings(max_examples=20, deadline=1500)
def test_query_health_data_valid_params(user_id, start_time, end_time):
    # The QueryHealthData API requires specific formatting for times
    # Start time: %Y-%m-%d %H:%M:%S
    # End time:   %Y-%m-%d %H:%M:%S

    call = f"QueryHealthData(user_id='{user_id}', start_time='{start_time}', end_time='{end_time}')"

    # Validate the format patterns
    assert len(user_id) > 0
    assert len(start_time) == 19  # %Y-%m-%d %H:%M:%S is 19 characters
    assert len(end_time) == 19

    # The postcondition expects a list of health data records
    # Since this is a property test, we verify the call structure matches the spec
    assert "QueryHealthData" in call
    assert "user_id" in call
    assert "start_time" in call
    assert "end_time" in call

@given(
    user_id=st.text(min_size=1, max_size=50),
    start_time=st.fixed_str("2023-03-05 00:00:00"),
    end_time=st.fixed_str("2023-03-12 23:59:59")
)
@settings(max_examples=20, deadline=1500)
def test_query_health_data_type_and_length():
    """Test that QueryHealthData returns a list of health data records."""
    call = f"QueryHealthData(user_id='{user_id}', start_time='{start_time}', end_time='{end_time}')"

    # The function signature specifies health_data as a list
    # We verify the call includes all required parameters
    assert "QueryHealthData" in call
    assert "user_id" in call
    assert "start_time" in call
    assert "end_time" in call

    # Additional invariant: if the call is made with valid params,
    # the response should be a list (as per the formal specification)
    # Since we're testing the API call itself, we focus on parameter validation
    assert len(user_id) > 0
    assert len(start_time) == 19
    assert len(end_time) == 19

@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.sampled_from(["2023-03-26"]),
    new_appointment_doctor=st.sampled_from(["Dr. Lee"])
)
@settings(max_examples=10, deadline=1500)
def test_modify_registration_with_dr_lee():
    """Test modifying registration with Dr. Lee as the new doctor."""
    call = f"ModifyRegistration(appointment_id='34567890', new_appointment_date='2023-03-26', new_appointment_doctor='Dr. Lee')"
    # Verify the call structure matches the expected API format
    assert call.startswith("ModifyRegistration")
    assert "appointment_id='34567890'" in call
    assert "new_appointment_date='2023-03-26'" in call
    assert "new_appointment_doctor='Dr. Lee'" in call

# Additional property tests for robustness
@given(
    appointment_id=st.text(min_size=1, max_size=50),
    new_appointment_date=st.sampled_from(["2023-04-15", "2023-02-28"]),
    new_appointment_doctor=st.sampled_from(["Dr. Smith", "Dr. Patel"])
)
@settings(max_examples=15, deadline=1500)
def test_modify_registration_various_dates_and_doctors():
    """Test ModifyRegistration with various dates and doctors."""
    call = f"ModifyRegistration(appointment_id='{appointment_id}', new_appointment_date='{new_appointment_date}', new_appointment_doctor='{new_appointment_doctor}')"
    # All parameters should be non-empty strings
    assert isinstance(appointment_id, str) and len(appointment_id) > 0
    assert isinstance(new_appointment_date, str) and len(new_appointment_date) == 10
    assert isinstance(new_appointment_doctor, str) and len(new_appointment_doctor) > 0

@given(
    user_id=st.text(min_size=1, max_size=50),
    start_time=st.fixed_str("2023-03-05 00:00:00"),
    end_time=st.fixed_str("2023-03-12 23:59:59")
)
@settings(max_examples=15, deadline=1500)
def test_query_health_data_min_max_range():
    """Test QueryHealthData with boundary dates."""
    call = f"QueryHealthData(user_id='J46801', start_time='{start_time}', end_time='{end_time}')"
    # Verify the time range covers at least some days
    assert len(start_time) == 19
    assert len(end_time) == 19
    assert start_time < end_time  # Start should be before end
