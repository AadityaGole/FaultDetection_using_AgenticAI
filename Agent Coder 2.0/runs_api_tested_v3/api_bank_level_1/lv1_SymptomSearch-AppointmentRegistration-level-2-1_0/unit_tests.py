from hypothesis import given, strategies as st
from evaluate.api_bank_evaluator import evaluate_api_bank

# Import the module containing evaluate_api_call
from __main__ import api_call

# The _api_bank_turn object from the generated implementation
_api_bank_turn = {
    "task_id": "lv1_SymptomSearch-AppointmentRegistration-level-2-1",
    "level": 1,
    "dialogue_id": "SymptomSearch-AppointmentRegistration-level-2-1",
    "turn_id": 0,
    "api_descriptions": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n"
        "The current year is 2023.\n"
        "Input: \nUser: User's utterence\nAI: AI's response\n\n"
        "Expected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\n"
        "API descriptions:\n{\"name\": \"SymptomSearch\", \"description\": \"This API searches for a given symptom.\", "
        "\"input_parameters\": {\"symptom\": {\"type\": \"str\", \"description\": \"The symptom to search.\"}}, "
        "\"output_parameters\": {\"results\": {\"type\": \"list\", \"description\": \"The list of results...\"}},\n"
        "{\"name\": \"AppointmentRegistration\", \"description\": \"This API registers an appointment of hospital.\", "
        "\"input_parameters\": {\"patient_name\": {\"type\": \"str\"}, \"date\": {\"type\": \"str\", \"description\": \"The date...\"}, \"doctor_name\": {\"type\": \"str\"}}, "
        "\"output_parameters\": {\"appointment_id\": {\"type\": \"str\"}}}"
    ),
    "dialogue_history": [],
    "expected_api_name": "SymptomSearch",
    "expected_param_dict": {"symptom": "fatigue"},
    "prompt": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n"
        "The current year is 2023.\n"
        "Input: \nUser: User's utterence\nAI: AI's response\n\n"
        "Expected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\n"
        "API descriptions: ..."
    )
}

def _generate_api_call(symptom=None, api_name=None, api_params=None):
    """Helper to construct a candidate API call string."""
    if api_name is None:
        # Default to SymptomSearch with symptom parameter
        return f"[SymptomSearch(key1='{symptom}')]"
    elif api_params is None:
        return "[SymptomSearch(key1='{symptom}', key2='some_value'))]"
    else:
        return f"[{api_name}(key1='{symptom}', key2='some_value'))]"

class TestEvaluateApiCall:
    """Tests for evaluate_api_call function."""

    def test_successful_symptomsearch_call(self):
        """Test successful evaluation with correct SymptomSearch call."""
        # Construct the expected API call string
        call = self._generate_api_call(symptom="fatigue")
        result = evaluate_api_call(call=call)
        # The evaluator should return True for a valid call
        assert result is True

    def test_case_insensitive_api_name_matches(self):
        """Test that API name matching is case-insensitive."""
        # Original expected API name is "SymptomSearch"
        call_upper = "[SymptomSEARCH](key1='fatigue')"
        call_lower = "[symptomsearch](key1='fatigue')"
        call_mixed = "[SymTomSearch](key1='fatigue')"

        # These should all be accepted (the evaluator normalizes case)
        result_upper = evaluate_api_call(call=call_upper)
        result_lower = evaluate_api_call(call=call_lower)
        result_mixed = evaluate_api_call(call=call_mixed)

        # All should pass (True) since the evaluator handles case-insensitivity
        assert result_upper is True
        assert result_lower is True
        assert result_mixed is True

    @given(
        symptom=st.text(min_size=1),
        api_name=st.sampled_from(["SymptomSearch", "AppointmentRegistration"]),
        api_params=st.just({"symptom": symptom})
    )
    def test_various_valid_calls(self, symptom, api_name, api_params):
        """Property test: various valid combinations should pass."""
        call = f"[{api_name}(key1='{symptom}')]"
        result = evaluate_api_call(call=call)
        assert result is True

    def test_missing_required_parameter_fails(self):
        """Test that missing required 'symptom' parameter causes failure."""
        # Call without symptom parameter
        call = "[SymptomSearch()]"
        result = evaluate_api_call(call=call)
        # Should fail because symptom is required
        assert result is False

    def test_wrong_api_name_fails(self):
        """Test that non-matching API name fails."""
        call = "[HeartDisease(key1='chest_pain'))]"
        result = evaluate_api_call(call=call)
        assert result is False

    def test_invalid_api_name_format_fails(self):
        """Test that malformed API name doesn't pass."""
        call = "[Invalid(API)(key1='fatigue'))]"
        result = evaluate_api_call(call=call)
        assert result is False

    def test_non_str_symptom_type_fails(self):
        """Test that non-string symptom value fails type validation."""
        call = "[SymptomSearch(key1='123'))]"  # numeric instead of string
        result = evaluate_api_call(call=call)
        assert result is False

    def test_empty_symptom_fails(self):
        """Test that empty symptom string fails."""
        call = "[SymptomSearch(key1=''))]"
        result = evaluate_api_call(call=call)
        assert result is False

    def test_whitespace_variations_pass(self):
        """Property test: whitespace variations should be normalized."""
        # Various whitespace patterns should still parse correctly
        variants = [
            "[ SymptomSearch (key1='fatigue') ]",
            "[SymptomSearch(key1='fatigue') ]",
            "[SymptomSearch (key1='fatigue')]",
        ]
        for variant in variants:
            result = evaluate_api_call(call=variant)
            assert result is True

    def test_different_apps_still_work(self):
        """Test that AppointmentRegistration with valid parameters passes."""
        call = "[AppointmentRegistration(patient_name='John Doe', date='2023-05-15', doctor_name='Dr. Smith'))"
        result = evaluate_api_call(call=call)
        assert result is True

    def test_invalid_date_format_fails(self):
        """Test that unrecognized date format is rejected."""
        call = "[SymptomSearch(key1='fatigue', date='not-a-date'))]"
        result = evaluate_api_call(call=call)
        assert result is False

    def test_none_candidate_uses_default(self):
        """When candidate is None, evaluate_api_call should use default."""
        result = evaluate_api_call()
        # Should fall back to default behavior (likely returns False or raises)
        # Based on the implementation, api_call() would be called with no args
        # The evaluator should handle this gracefully
        # We just verify it doesn't crash
        assert result is not None

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
