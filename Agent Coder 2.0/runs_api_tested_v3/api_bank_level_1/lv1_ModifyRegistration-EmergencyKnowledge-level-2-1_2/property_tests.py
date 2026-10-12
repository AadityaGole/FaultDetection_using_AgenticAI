from hypothesis import given, strategies as st, settings, assume

# Strategy for valid appointment IDs (non-empty strings)
appointment_id_str = st.text(min_size=1, max_size=50)

# Strategy for valid dates in YYYY-MM-DD format
def _date_dict(d):
    return {
        'year': d['year'],
        'month': d['month'],
        'day': d['day']
    }

date_str = st.dictionaries(
    'year', st.integers(min_value=1900, max_value=2100),
    'month', st.integers(min_value=1, max_value=12),
    'day', st.integers(min_value=1, max_value=31)
)

# Strategy for valid doctor names (non-empty strings)
doctor_str = st.text(min_size=1, max_size=50)

# Full valid ModifyRegistration call with all required parameters
valid_modify_registration = st.dict(
    api_name='ModifyRegistration',
    appointment_id=appointment_id_str,
    new_appointment_date=date_str,
    new_appointment_doctor=doctor_str
)

@given(valid_modify_registration)
@settings(max_examples=20, deadline=1500)
def test_valid_modify_registration(call):
    """Test that valid ModifyRegistration calls are parsed correctly and return a status field."""
    result = evaluate_api_call(call)

    # Result must be a dictionary
    assert isinstance(result, dict), "Result must be a dictionary"

    # Must contain a status field
    assert 'status' in result, "Result must contain a 'status' field"

    # Status must be either 'success' or 'failure'
    assert result['status'] in ('success', 'failure'), \
        f"Status must be 'success' or 'failure', got {result['status']!r}"

@given(valid_modify_registration)
@settings(max_examples=20, deadline=1500)
def test_valid_modify_registration_contains_status(call):
    """Ensure the response always contains the expected status field."""
    result = evaluate_api_call(call)
    assert 'status' in result, "Missing 'status' field in response"

# Tests for invalid API names (case insensitivity and wrong identifiers)
invalid_api_names = [
    "modifieregistration",
    "modify_registration",
    "ModifyRegistration",
    "modify registration",
    "",  # empty string
    None,  # None value
]

for bad_name in invalid_api_names:
    @given()
    @settings(max_examples=1, deadline=500)
    def test_invalid_api_name(bad_name):
        call = {
            'api_name': bad_name,
            'appointment_id': '12345',
            'new_appointment_date': '2023-04-15',
            'new_appointment_doctor': 'Dr. Smith'
        }
        try:
            result = evaluate_api_call(call)
            # Should fail on malformed API name (case-sensitive mismatch or wrong identifier)
            assert False, f"Expected
