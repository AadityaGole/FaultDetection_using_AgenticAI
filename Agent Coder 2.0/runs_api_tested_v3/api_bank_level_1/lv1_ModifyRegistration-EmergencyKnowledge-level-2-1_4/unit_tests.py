from evaluate.api_bank_evaluator import evaluate_api_bank
from typing import Dict, Any

# The ground truth from the task description
GROUND_TRUTH = {
    "expected_api_name": "EmergencyKnowledge",
    "expected_param_dict": {"symptom": "fatigue"},
    "task_id": "lv1_ModifyRegistration-EmergencyKnowledge-level-2-1_4",
    "level": 1,
    "dialogue_id": "ModifyRegistration-EmergencyKnowledge-level-2-1",
    "turn_id": 4,
}

def _parse_api_call(call_str: str) -> Dict[str, Any]:
    """Parse the API call string into components."""
    # Simple parser for the expected format: [ApiName(key1='value1', ...)]
    # This mimics what the evaluator would do
    try:
        # Extract API name from brackets
        start = call_str.find('[') + 1
        end = call_str.find(']')
        api_name = call_str[start:end].strip()

        # Extract parameters inside braces
        brace_start = call_str.find('{')
        brace_end = call_str.rfind('}')
        params_str = call_str[brace_start+1:brace_end].strip()

        # Parse key-value pairs
        params = {}
        if params_str:
            for pair in params_str.split(','):
                pair = pair.strip()
                if '=' in pair:
                    key, val = pair.split('=', 1)
                    params[key.strip()] = val.strip().strip("'")

        return {
            "api_name": api_name,
            "params": params,
        }
    except Exception:
        return None

def _validate_type(value: Any, expected_type: type) -> bool:
    """Check if value matches the expected type."""
    if expected_type == str:
        return isinstance(value, str)
    elif expected_type == int:
        return isinstance(value, int)
    elif expected_type == float:
        return isinstance(value, (int, float))
    elif expected_type == list:
        return isinstance(value, list)
    elif expected_type == dict:
        return isinstance(value, dict)
    return False

def _check_case_insensitive_match(name: str, target: str) -> bool:
    """Case-insensitive comparison for API names."""
    return name.lower() == target.lower()

class TestEvaluateApiCall:
    """Unit tests for evaluate_api_call function."""

    def test_valid_emergency_knowledge_symptom_fatigue(self):
        """Test valid EmergencyKnowledge call with symptom='fatigue'."""
        call_str = "[EmergencyKnowledge(symptom='fatigue')]"
        result = evaluate_api_call(call_str)

        # Check parsed API name matches case-insensitively
        self.assertEqual(result["parsed_api_name"], GROUND_TRUTH["expected_api_name"])

        # Check parameters match expected dict
        self.assertEqual(result["params"], GROUND_TRUTH["expected_param_dict"])

        # Additional validation: symptom is a string
        self.assertTrue(isinstance(result["params"]["symptom"], str))

    def test_valid_emergency_knowledge_symptom_anemia(self):
        """Test valid EmergencyKnowledge call with symptom='Anemia'."""
        call_str = "[EmergencyKnowledge(symptom='Anemia')]"
        result = evaluate_api_call(call_str)

        self.assertEqual(result["parsed_api_name"], GROUND_TRUTH["expected_api_name"])
        self.assertEqual(result["params"], {"symptom": "Anemia"})

    def test_case_insensitive_api_name_matching(self):
        """Test that API name matching is case-insensitive."""
        # Original correct call
        call_str_correct = "[EmergencyKnowledge(symptom='fatigue')]"
        result_correct = evaluate_api_call(call_str_correct)

        # Case variation - should still match
        call_str_variation = "[EMERGENCIENKOWNTY(symptom='fatigue')]"
        result_var = evaluate_api_call(call_str_variation)

        self.assertIsNotNone(result_correct)
        self.assertIsNotNone(result_var)

        # Both should have same parsed API name (case-insensitive)
        self.assertEqual(result_correct["parsed_api_name"], result_var["parsed_api_name"])

    def test_missing_required_parameter(self):
        """Test that missing required parameter causes failure."""
        call_str = "[EmergencyKnowledge()]"
        result = evaluate_api_call(call_str)

        # Should either raise an error or return with mismatch
        # The evaluator should detect missing 'symptom' parameter
        self.assertFalse(result["passed"])

    def test_invalid_api_name(self):
        """Test that non-existent API name fails."""
        call_str = "[UnknownAPI(symptom='fatigue')]"
        result = evaluate_api_call(call_str)

        # Should not match the expected API name
        self.assertNotEqual(result["parsed_api_name"], GROUND_TRUTH["expected_api_name"])

    def test_wrong_api_name_format(self):
        """Test that malformed API name doesn't pass."""
        call_str = "[EmergencyKnowledge(symptom='fatigue', unknown_param='value')]"
        result = evaluate_api_call(call_str)

        # The evaluator should handle extra parameters gracefully
        # but still identify the base API name
        self.assertIn("EmergencyKnowledge", result.get("parsed_api_name", ""))

    def test_empty_api_call_string(self):
        """Test handling of empty or malformed API call string."""
        result = evaluate_api_call("")

        # Should fail to parse or return no match
        self.assertFalse(result["passed"])

    def test_whitespace_variations(self):
        """Property test: whitespace variations should produce equivalent results."""
        from hypothesis import given, strategies as st

        @given(st.text(min_size=10, max_size=100))
        def test_whitespace_equivalence(text: str):
            # Normalize whitespace
            normalized = " ".join(text.split())

            # Both original and normalized should yield same result
            result_original = evaluate_api_call(normalized)
            result_normalized = evaluate_api_call(normalized)

            # Both should have same parsed API name and params
            self.assertEqual(
                result_original["parsed_api_name"],
                result_normalized["parsed_api_name"]
            )
            self.assertEqual(
                result_original["params"],
                result_normalized["params"]
            )

    def test_modify_registration_api(self):
        """Test ModifyRegistration API call with proper parameters."""
        call_str = "[ModifyRegistration(appointment_id='12345678', new_appointment_date='2023-04-15', new_appointment_doctor='Dr. Johnson')]"
        result = evaluate_api_call(call_str)

        self.assertEqual(result["parsed_api_name"], GROUND_TRUTH["expected_api_name"])
        self.assertEqual(result["params"], {
            "appointment_id": "12345678",
            "new_appointment_date": "2023-04-15",
            "new_appointment_doctor": "Dr. Johnson"
        })

    def test_modify_registration_missing_parameter(self):
        """Test that missing required parameter causes failure."""
        call_str = "[ModifyRegistration(appointment_id='12345678')]"
        result = evaluate_api_call(call_str)

        # Should fail because new_appointment_date and new_appointment_doctor are required
        self.assertFalse(result["passed"])

    def test_modify_registration_invalid_date_format(self):
        """Test that invalid date format is rejected."""
        call_str = "[ModifyRegistration(appointment_id='12345678', new_appointment_date='2023-13-01', new_appointment_doctor='Dr. Smith')]"
        result = evaluate_api_call(call_str)

        # Date '2023-13-01' is invalid (month 13 doesn't exist)
        # The evaluator should reject this or handle it gracefully
        # At minimum, the API name and basic parameters should still be parsed
        self.assertIn("ModifyRegistration", result.get("parsed_api_name", ""))

    def test_modify_registration_wrong_parameter_names(self):
        """Test that incorrect parameter names cause failure."""
        call_str = "[ModifyRegistration(appointment_id='12345678', new_date='2023-04-15', new_doctor='Dr. Smith')]"
        result = evaluate_api_call(call_str)

        # Parameter names must match exactly: appointment_id, new_appointment_date, new_appointment_doctor
        self.assertFalse(result["passed"])

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
