from hypothesis import given, strategies as st
from evaluate.api_bank_evaluator import evaluate_api_bank
from dataset.api_bank_loader import APIBankTurn

# Recreate the minimal environment needed for testing
_api_bank_turn = {
    "task_id": "test_modify_registration",
    "level": 1,
    "dialogue_id": "ModifyRegistration-level-2-2",
    "turn_id": 4,
    "api_descriptions": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n"
        "The current year is 2023.\n"
        "Input: \nUser: User's utterence\nAI: AI's response\n\nExpected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\nAPI descriptions:\n{\"name\": \"QueryHealthData\", ...}\n{\"name\": \"CancelRegistration\", ...}\n{\"name\": \"ModifyRegistration\", ...}"
    ),
    "expected_api_name": "CancelRegistration",
    "expected_param_dict": {"appointment_id": "90123456"},
}

def _generate_api_call():
    """Simulates the _generated_api_call from the task."""
    return "[CancelRegistration(appointment_id='90123456')]"

def evaluate_api_call(candidate=None):
    output = _generate_api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn, output)

class TestEvaluateApiCall:
    """Tests for evaluate_api_call function."""

    def test_correct_modify_registration_call(self):
        """Test a valid ModifyRegistration API call."""
        # Correct call with required parameters
        call = "[ModifyRegistration(appointment_id='34567890', new_appointment_date='2023-03-26', new_appointment_doctor='Dr. Lee')]"
        result = evaluate_api_call(call)
        self.assertIsNotNone(result)
        # Verify the evaluator parses correctly
        parsed = evaluate_api_bank(_api_bank_turn, call)
        self.assertEqual(parsed["api_name"], "modifierestriction")  # Should be case-insensitive match
        self.assertEqual(parsed["params"], {
            "appointment_id": "34567890",
            "new_appointment_date": "2023-03-26",
            "new_appointment_doctor": "Dr. Lee"
        })

    def test_correct_cancel_registration_call(self):
        """Test a valid CancelRegistration API call."""
        call = "[CancelRegistration(appointment_id='90123456')]"
        result = evaluate_api_call(call)
        self.assertIsNotNone(result)
        parsed = evaluate_api_bank(_api_bank_turn, call)
        self.assertEqual(parsed["api_name"], "cancelregistration")
        self.assertEqual(parsed["params"], {"appointment_id": "90123456"})

    def test_correct_query_health_data_call(self):
        """Test a valid QueryHealthData API call."""
        call = "[QueryHealthData(user_id='J46801', start_time='2023-03-05 00:00:00', end_time='2023-03-12 00:00:00')]"
        result = evaluate_api_call(call)
        self.assertIsNotNone(result)
        parsed = evaluate_api_bank(_api_bank_turn, call)
        self.assertEqual(parsed["api_name"], "queryhealthdata")
        self.assertEqual(parsed["params"], {
            "user_id": "J46801",
            "start_time": "2023-03-05 00:00:00",
            "end_time": "2023-03-12 00:00:00"
        })

    def test_case_insensitive_api_name_matching(self):
        """Test that API names are matched case-insensitively."""
        # Lowercase variant should still work
        call_lower = "[modifierestriction(appointment_id='12345')]"
        result = evaluate_api_call(call_lower)
        self.assertIsNotNone(result)
        parsed = evaluate_api_bank(_api_bank_turn, call_lower)
        self.assertEqual(parsed["api_name"], "modifierestriction")

    def test_wrong_api_name_fails(self):
        """Test that a non-existent API name fails."""
        call = "[InvalidAPI(appointment_id='123')]"
        result = evaluate_api_call(call)
        # Should either raise an error or return a failure indicator
        # The evaluator should reject unknown API names
        self.assertFalse(result)  # Or appropriate failure indication

    def test_missing_required_param_fails(self):
        """Test that missing required parameters cause failure."""
        # Only providing appointment_id but missing others
        call = "[ModifyRegistration(appointment_id='123')]"
        result = evaluate_api_call(call)
        # Should fail due to missing required parameters
        self.assertFalse(result)

    def test_extra_unrecognized_param_fails(self):
        """Test that unrecognized parameters are rejected."""
        call = "[ModifyRegistration(appointment_id='123', extra_field='ignored')]"
        result = evaluate_api_call(call)
        # Should fail because extra field is not in the schema
        self.assertFalse(result)

    @given(st.text(min_size=1), st.text(min_size=1))
    def test_hypothesis_valid_cancel_registration_variations(self, appointment_id, appointment_id_str):
        """Property test: various valid CancelRegistration calls."""
        call = f"[CancelRegistration(appointment_id='{appointment_id}')]"
        result = evaluate_api_call(call)
        self.assertIsNotNone(result)
        parsed = evaluate_api_bank(_api_bank_turn, call)
        self.assertEqual(parsed["api_name"], "cancelregistration")
        self.assertEqual(parsed["params"], {"appointment_id": appointment_id})

    @given(st.text(min_size=1), st.text(min_size=1), st.text(min_size=1))
    def test_hypothesis_valid_modify_registration_variations(self, appointment_id, new_date, new_doctor):
        """Property test: various valid ModifyRegistration calls."""
        call = f"[ModifyRegistration(appointment_id='{appointment_id}', new_appointment_date='{new_date}', new_appointment_doctor='{new_doctor}')]"
        result = evaluate_api_call(call)
        self.assertIsNotNone(result)
        parsed = evaluate_api_bank(_api_bank_turn, call)
        self.assertEqual(parsed["api_name"], "modifierestriction")
        self.assertEqual(parsed["params"], {
            "appointment_id": appointment_id,
            "new_appointment_date": new_date,
            "new_appointment_doctor": new_doctor
        })

    @given(st.text(min_size=1), st.text(min_size=1))
    def test_hypothesis_invalid_date_format_fails(self, start_time, end_time):
        """Property test: invalid date formats should cause failure."""
        # These should fail because dates don't match the expected format
        bad_dates = [
            "2023-13-01",      # Invalid month
            "2023-02-30",       # Invalid day
            "2023-03-05 25:00:00",  # Invalid hour
            "not-a-date",
        ]
        for date_str in bad_dates:
            call = f"[QueryHealthData(start_time='{date_str}', end_time='2023-03-12 00:00:00')]"
            result = evaluate_api_call(call)
            # Should fail due to invalid date format
            self.assertFalse(result)

    @given(st.text(min_size=1))
    def test_empty_and_whitespace_cases(self):
        """Test edge cases with empty or whitespace-only inputs."""
        # Empty string should fail
        call = "[CancelRegistration()]"
        result = evaluate_api_call(call)
        self.assertFalse(result)

        # Whitespace-only should fail
        call = "[CancelRegistration(appointment_id=' ')]"
        result = evaluate_api_call(call)
        self.assertFalse(result)

    def test_can_cancel_without_other_params(self):
        """Test CancelRegistration with just appointment_id works."""
        call = "[CancelRegistration(appointment_id='987654321')]"
        result = evaluate_api_call(call)
        self.assertIsNotNone(result)
        parsed = evaluate_api_bank(_api_bank_turn, call)
        self.assertEqual(parsed["api_name"], "cancelregistration")
        self.assertEqual(parsed["params"], {"appointment_id": "987654321"})

if __name__ == "__main__":
    import sys
    try:
        # Run the tests
        import unittest
        suite = unittest.TestLoader().loadTestsFromTestCase(TestEvaluateApiCall)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    except Exception as e:
        print(f"Test failed with exception: {e}")
        sys.exit(1)
