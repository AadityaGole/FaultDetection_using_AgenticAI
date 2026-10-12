from hypothesis import given, strategies as st
from evaluation.api_bank_evaluator import evaluate_api_bank
from dataset.api_bank_loader import APIBankTurn

# The global _api_bank_turn is defined in the implementation
# We'll import it from the same module structure

def _get_api_turn():
    """Helper to get the _api_bank_turn object used by the evaluator."""
    # In the actual implementation, this would be imported
    # Here we assume it's available via the global scope
    return __import__('dataset.api_bank_loader').APIBankTurn(
        **json.loads('{"task_id": "lv1_ModifyRegistration-EmergencyKnowledge-level-2-1", "level": 1, "dialogue_id": "ModifyRegistration-EmergencyKnowledge-level-2-1", "turn_id": 2, "api_descriptions": "...", "dialogue_history": [], "expected_api_name": "EmergencyKnowledge", "expected_param_dict": {"symptom": "fatigue"}, "prompt": "..."}')

# Actually, looking more carefully at the setup, the _api_bank_turn is defined globally
# in the implementation file. Since we're testing evaluate_api_call which uses it,
# we need to ensure it's accessible. Let me adjust the approach.

# The evaluate_api_call function uses _api_bank_turn from the global scope.
# We'll call it directly through the provided interface.

import json
from evaluation.api_bank_evaluator import evaluate_api_bank

# Recreate the turn data as it appears in the original implementation
api_turn_data = {
    "task_id": "lv1_ModifyRegistration-EmergencyKnowledge-level-2-1",
    "level": 1,
    "dialogue_id": "ModifyRegistration-EmergencyKnowledge-level-2-1",
    "turn_id": 2,
    "api_descriptions": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n"
        "The current year is 2023.\n"
        "Input: \nUser: User's utterence\nAI: AI's response\n\n"
        "Expected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\n"
        "API descriptions:\n{\"name\": \"EmergencyKnowledge\", \"description\": \"This API searches for a given symptom for emergency knowledge.\", ..."
    ),
    "dialogue_history": [],
    "expected_api_name": "EmergencyKnowledge",
    "expected_param_dict": {"symptom": "fatigue"},
    "prompt": "Generate an API request..."
}

# Create the turn object
_api_bank_turn = type('_BankTurn', (), {})()
for key, value in api_turn_data.items():
    setattr(_api_bank_turn, key, value)

def evaluate_api_call(candidate=None):
    """Wrapper around the provided entry point."""
    return evaluate_api_call(candidate)

# Now write the tests

def test_successful_emergency_knowledge_fatigue():
    """Test successful EmergencyKnowledge call with symptom='fatigue'."""
    # This should produce a valid API request
    candidate = "[EmergencyKnowledge(symptom='fatigue')]"
    result = evaluate_api_call(candidate)
    # The evaluator returns a dict with api_match, params_match, etc.
    # We need to check the parsed components
    assert result["api_match"] == True
    # Check that the symptom parameter was correctly extracted and matched
    # The evaluator should parse the API name and parameters
    # Verify the API name is correct (case-insensitive match)
    assert "EmergencyKnowledge" in result.get("api_name", "")
    # Verify the symptom parameter exists and matches
    assert "symptom" in result.get("params", {})
    assert result["params"]["symptom"] == "fatigue"

def test_successful_modify_registration():
    """Test successful ModifyRegistration call with all required parameters."""
    candidate = "[ModifyRegistration(appointment_id='12345678', new_appointment_date='2023-04-15', new_appointment_doctor='Dr. Johnson')]"
    result = evaluate_api_call(candidate)
    assert result["api_match"] == True
    assert "ModifyRegistration" in result.get("api_name", "")
    # All three required parameters should be present
    params = result.get("params", {})
    assert "appointment_id" in params
    assert "new_appointment_date" in params
    assert "new_appointment_doctor" in params
    # Type checking: all should be strings
    assert isinstance(params["appointment_id"], str)
    assert isinstance(params["new_appointment_date"], str)
    assert isinstance(params["new_appointment_doctor"], str)

def test_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    # Try different casings of the same API name
    candidates = [
        "[EmergencyKnowledge(symptom='fatigue')]",
        "[emergencyscience(symptom='fatigue')]",
        "[EMERGENCYKNOWLEDGE(symptom='fatigue')]",
    ]
    for candidate in candidates:
        result = evaluate_api_call(candidate)
        assert result["api_match"] == True
        assert "EmergencyKnowledge" in result.get("api_name", "").lower()

def test_missing_required_parameter():
    """Test that missing required parameters cause failure."""
    # Missing symptom for EmergencyKnowledge
    candidate = "[EmergencyKnowledge()]"
    result = evaluate_api_call(candidate)
    # Should fail to match due to missing required parameter
    assert result["api_match"] == False

def test_invalid_date_format():
    """Test that non-YYYY-MM-DD dates are rejected."""
    # Various invalid date formats
    invalid_dates = ["2023/04/15", "04-15-2023", "2023-13-45", "invalid"]
    for date_str in invalid_dates:
        candidate = f"[ModifyRegistration(appointment_id='12345678', new_appointment_date='{date_str}', new_appointment_doctor='Dr. Johnson')]"
        result = evaluate_api_call(candidate)
        # Should fail because date doesn't match YYYY-MM-DD pattern
        assert result["api_match"] == False

def test_wrong_api_name():
    """Test that calling a non-existent API fails."""
    candidate = "[UnknownAPI(symptom='fatigue')]"
    result = evaluate_api_call(candidate)
    assert result["api_match"] == False

def test_whitespace_variations_hypothesis():
    """Use Hypothesis to test that whitespace variations still parse correctly."""
    # These should all parse the same way despite extra spaces
    whitespace_candidates = [
        "[EmergencyKnowledge(symptom='fatigue')]",
        "[EmergencyKnowledge (symptom='fatigue') ]",
        "[  EmergencyKnowledge  (symptom='fatigue')  ]",
        "[EmergencyKnowledge(symptom='fatigue') ]",
    ]
    for candidate in whitespace_candidates:
        result = evaluate_api_call(candidate)
        assert result["api_match"] == True
        assert "EmergencyKnowledge" in result.get("api_name", "")

def test_empty_symptom():
    """Test handling of empty symptom string."""
    candidate = "[EmergencyKnowledge(symptom='')]"
    result = evaluate_api_call(candidate)
    # Empty string might be considered valid but could be flagged
    # At minimum, the API should parse without error
    assert "EmergencyKnowledge" in result.get("api_name", "")

def test_minimal_valid_call():
    """Test the minimal valid call structure."""
    candidate = "[EmergencyKnowledge(symptom='test')]"
    result = evaluate_api_call(candidate)
    assert result["api_match"] == True
    assert "symptom" in result.get("params", {})

if __name__ == "__main__":
    # Run the tests
    test_successful_emergency_knowledge_fatigue()
    test_successful_modify_registration()
    test_case_insensitive_api_name()
    test_missing_required_parameter()
    test_invalid_date_format()
    test_wrong_api_name()
    test_whitespace_variations_hypothesis()
    test_empty_symptom()
    test_minimal_valid_call()
    print("All tests passed!")
