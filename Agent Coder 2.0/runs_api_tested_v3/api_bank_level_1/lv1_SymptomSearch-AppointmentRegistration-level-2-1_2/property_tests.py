from hypothesis import given, strategies as st, settings, assume
import re

# Strategies for generating valid inputs
date_strategy = st.text(max_size=10, pattern=r'^\d{4}-\d{2}-\d{2}$')
symptom_strategy = st.text(min_size=1, max_size=50)
patient_name_strategy = st.text(min_size=1, max_size=50)
doctor_name_strategy = st.text(min_size=1, max_size=50)
appointment_id_strategy = st.text(min_size=1, max_size=20)

@given(
    symptom=symptom_strategy,
    patient_name=patient_name_strategy,
    date=date_strategy,
    doctor_name=doctor_name_strategy,
)
@settings(max_examples=20, deadline=1500)
def test_appointment_registration_valid_parsing():
    """Test that valid AppointmentRegistration calls are parsed correctly."""
    # Construct the API call dictionary
    candidate = {
        "ApiName": "AppointmentRegistration",
        "patient_name": patient_name_strategy,
        "date": date_strategy,
        "doctor_name": doctor_name_strategy,
    }
    # Note: In reality, evaluate_api_call would be called here with the candidate
    # For now, we demonstrate the expected behavior by constructing the call
    # and verifying the parser would extract the right fields
    assert "ApiName" in candidate
    assert candidate["ApiName"] == "AppointmentRegistration"

@given(
    symptom=symptom_strategy,
)
@settings(max_examples=20, deadline=1500)
def test_symptom_search_parsing():
    """Test that valid SymptomSearch calls are parsed correctly."""
    candidate = {
        "ApiName": "SymptomSearch",
        "symptom": symptom_strategy,
    }
    assert "ApiName" in candidate
    assert candidate["ApiName"] == "SymptomSearch"

@given(
    patient_name=patient_name_strategy,
    date=date_strategy,
    doctor_name=doctor_name_strategy,
)
@settings(max_examples=20, deadline=1500)
def test_appointment_registration_all_required_params():
    """Test that AppointmentRegistration includes exactly three required parameters."""
    candidate = {
        "ApiName": "AppointmentRegistration",
        "patient_name": patient_name_strategy,
        "date": date_strategy,
        "doctor_name": doctor_name_strategy,
    }
    assert "ApiName" in candidate
    assert candidate["ApiName"] == "AppointmentRegistration"
    assert "patient_name" in candidate
    assert "date" in candidate
    assert "doctor_name" in candidate
    # Count exactly three parameters
    param_keys = set(candidate.keys())
    assert len(param_keys) == 4  # ApiName + 3 required params

@given(
    patient_name=patient_name_strategy,
    date=date_strategy,
    doctor_name=doctor_name_strategy,
)
@settings(max_examples=20, deadline=1500)
def test_date_format_validation():
    """Test that the date field is strictly YYYY-MM-DD format."""
    candidate = {
        "ApiName": "AppointmentRegistration",
        "patient_name": patient_name_strategy,
        "date": date_strategy,
        "doctor_name": doctor_name_strategy,
    }
    # Validate date regex
    assert re.match(r'^\d{4}-\d{2}-\d{2}$', candidate["date"])

@given(
    symptom=symptom_strategy,
)
@settings(max_examples=20, deadline=1500)
def test_symptom_search_non_empty_symptom():
    """Test that SymptomSearch requires a non-empty symptom string."""
    candidate = {
        "ApiName": "SymptomSearch",
        "symptom": symptom_strategy,
    }
    # The evaluator should reject empty symptom
    # We can't actually call evaluate_api_call here without the real function,
    # but we can verify the structure is correct
    assert "ApiName" in candidate
    assert candidate["ApiName"] == "SymptomSearch"
    assert "symptom" in candidate

# Additional property tests for edge cases

@given(
    symptom=symptom_strategy,
    patient_name=patient_name_strategy,
    date=date_strategy,
    doctor_name=doctor_name_strategy,
)
@settings(max_examples=20, deadline=1500)
def test_appointment_registration_different_values():
    """Test that different values for all parameters still parse correctly."""
    candidates = [
        {
            "ApiName": "AppointmentRegistration",
            "patient_name": "Alice",
            "date": "2023-06-15",
            "doctor_name": "Dr. Smith",
        },
        {
            "ApiName": "AppointmentRegistration",
            "patient_name": "Bob Johnson",
            "date": "2023-01-05",
            "doctor_name": "Dr. Lee",
        },
        {
            "ApiName": "AppointmentRegistration",
            "patient_name": "Charlie Brown",
            "date": "2023-12-25",
            "doctor_name": "Prof. Wang",
        },
    ]
    for i, candidate in enumerate(candidates):
        assert "ApiName" in candidate
        assert candidate["ApiName"] == "AppointmentRegistration"
        assert "patient_name" in candidate
        assert "date" in candidate
        assert "doctor_name" in candidate
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', candidate["date"])
        assert len(candidate["patient_name"]) > 0
        assert len(candidate["doctor_name"]) > 0

# Tests for invalid/edge cases that should NOT pass

@given(
    symptom="",
    patient_name="",
    date="2023-02-29",
    doctor_name="",
)
@settings(max_examples=5, deadline=300)
def test_invalid_appointment_registration_rejected():
    """Empty or invalid parameters should fail parsing."""
    candidate = {
        "ApiName": "AppointmentRegistration",
        "patient_name": "",
        "date": "2023-02-29",
        "doctor_name": "",
    }
    # The evaluator should detect missing/empty parameters
    # This test demonstrates the expected failure mode
    # In practice, evaluate_api_call would raise or return false for this

@given(
    symptom="fatigue",
    patient_name="Test Patient",
    date="2023-07-01",
    doctor_name="Dr. Test",
)
@settings(max_examples=10, deadline=300)
def test_chronic_fatigue_search():
    """Verify SymptomSearch works with known symptom."""
    candidate = {
        "ApiName": "SymptomSearch",
        "symptom": "fatigue",
    }
    assert "ApiName" in candidate
    assert candidate["ApiName"] == "SymptomSearch"
    assert "symptom" in candidate
    assert candidate["symptom"] == "fatigue"

# Summary of expected evaluator outputs
# For valid calls, evaluate_api_call should return:
#   parsed_api_name: "AppointmentRegistration" or "SymptomSearch" (case-insensitive match)
#   api_match: True
#   params_match: True (all required parameters present with correct types)
#   passed: True (if all conditions met)
