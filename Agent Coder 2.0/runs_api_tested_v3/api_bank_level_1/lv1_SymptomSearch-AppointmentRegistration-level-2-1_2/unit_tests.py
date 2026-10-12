from evaluate.api_bank_evaluator import evaluate_api_bank

# Recreate the _api_bank_turn as defined in the generated implementation
_api_bank_turn = {
    "task_id": "lv1_SymptomSearch-AppointmentRegistration-level-2-1",
    "level": 1,
    "dialogue_id": "SymptomSearch-AppointmentRegistration-level-2-1",
    "turn_id": 2,
    "api_descriptions": (
        "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] "
        "based on the previous dialogue context.\n"
        "The current year is 2023.\n"
        "Input: \nUser: User's utterence\nAI: AI's response\n\n"
        "Expected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\n"
        "API descriptions:\n{\"name\": \"SymptomSearch\", \"description\": \"This API searches for a given symptom.\", "
        "\"input_parameters\": {\"symptom\": {\"type\": \"str\", \"description\": \"The symptom to search.\"}}," \
        "\"output_parameters\": {\"results\": {\"type\": \"list\", \"description\": \"The list of results...\"}}},\n"
        "{\"name\": \"AppointmentRegistration\", \"description\": \"This API registers an appointment of hospital.\","
    )
}

def test_valid_symptom_search_with_fatigue():
    """Test that a valid SymptomSearch call with symptom='fatigue' passes evaluation."""
    candidate = "[SymptomSearch(symptom='fatigue')]"
    result = evaluate_api_call(candidate)
    assert result == True

def test_valid_symptom_search_with_other_symptom():
    """Test another valid symptom search with a different symptom."""
    candidate = "[SymptomSearch(symptom='anemia')]"
    result = evaluate_api_call(candidate)
    assert result == True

def test_invalid_api_name_fails():
    """Test that an API name that doesn't match the allowed list fails."""
    candidate = "[InvalidAPI(symptom='fatigue')]"
    result = evaluate_api_call(candidate)
    assert result == False

def test_missing_required_symptom_parameter_fails():
    """Test that omitting the required 'symptom' parameter causes evaluation to fail."""
    candidate = "[SymptomSearch()]"
    result = evaluate_api_call(candidate)
    assert result == False

def test_non_string_symptom_parameter_fails():
    """Test that passing a non-string symptom value fails."""
    candidate = "[SymptomSearch(symptom=123)]"
    result = evaluate_api_call(candidate)
    assert result == False

def test_case_insensitive_api_name_match():
    """Test that API name matching is case-insensitive (e.g., 'symptumsearch' vs 'SymptomSearch')."""
    candidate_lower = "[symptom='fatigue')]"  # lowercase
    result_lower = evaluate_api_call(candidate_lower)
    candidate_upper = "[SymptomSearch(symptom='fatigue')]"
    result_upper = evaluate_api_call(candidate_upper)
    assert result_lower == True
    assert result_upper == True

def test_extra_unwanted_parameters_pass_if_optional():
    """Test that extra parameters beyond what's required don't break validation (if optional)."""
    # Assuming symptom is the only required parameter
    candidate = "[SymptomSearch(symptom='depression', extra_param='ignored')]"
    result = evaluate_api_call(candidate)
    # The evaluator should still pass if symptom is present and correctly typed
    assert result == True

def test_empty_symptom_value_fails():
    """Test that an empty string symptom fails (not a valid disease name)."""
    candidate = "[SymptomSearch(symptom='')]"
    result = evaluate_api_call(candidate)
    assert result == False

def test_nonexistent_symptom_returns_results():
    """Test that searching for a non-existent symptom still parses correctly (no crash)."""
    candidate = "[SymptomSearch(symptom='unknown_disease')]"
    result = evaluate_api_call(candidate)
    # Should not raise an exception and should return a boolean indicating success/failure
    assert isinstance(result, bool)
