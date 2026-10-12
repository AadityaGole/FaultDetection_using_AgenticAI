from hypothesis import given, strategies as st, settings, assume

# Strategy for valid appointment_id (non-empty string)
appointment_id_strategy = st.text(min_size=1, max_size=50)

# Strategy for valid date in YYYY-MM-DD format
# Using fixed dictionaries to generate valid dates within reasonable range
date_factory = {
    'year': st.integers(min_value=2020, max_value=2030),
    'month': st.integers(min_value=1, max_value=12),
    'day': st.integers(min_value=1, max_value=28),
}
date_strategy = date_factory.apply(lambda d: f"{d['year']}-{d['month']:02d}-{d['day']}")

# Strategy for valid doctor name (non-empty string)
doctor_strategy = st.text(min_size=1, max_size=30)

@settings(max_examples=20, deadline=1500)
@given(appointment_id_strategy, date_strategy, doctor_strategy)
def test_modify_registration_functional(appointment_id, new_appointment_date, new_appointment_doctor):
    """
    Test that ModifyRegistration API call is parsed correctly and returns a success status.
    """
    api_call = f"ModifyRegistration(appointment_id='{appointment_id}', new_appointment_date='{new_appointment_date}', new_appointment_doctor='{new_appointment_doctor}
