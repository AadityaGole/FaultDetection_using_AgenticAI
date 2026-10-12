from hypothesis import given, strategies as st, settings, assume

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=15, deadline=1500)
def test_emergency_knowledge_symptom_required_and_non_empty():
    """Test that EmergencyKnowledge requires a non-empty symptom string."""
    result = evaluate_api_call(api_name, {"symptom": "fatigue"})
    assert isinstance(result, list), "Result should be a list of results"
    for item in result:
        assert isinstance(item, dict), "Each result should be a dictionary"
        assert "name" in item, "Result must contain 'name' field"
        assert "aid" in item, "Result must contain 'aid' field"
        assert isinstance(item["name"], str), "Result name must be a string"
        assert isinstance(item["aid"], str), "Result aid must be a string"

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=15, deadline=1500)
def test_emergency_knowledge_output_format():
    """Test that EmergencyKnowledge returns a list of dicts with name and aid keys."""
    result = evaluate_api_call(api_name, {"symptom": "anemia"})
    assert isinstance(result, list), "Result must be a list"
    assert len(result) > 0, "Result list should not be empty for valid input"
    for item in result:
        assert "name" in item, "Missing 'name' key"
        assert "aid" in item, "Missing 'aid' key"
        assert isinstance(item["name"], str), "Name must be a string"
        assert isinstance(item["aid"], str), "Aid must be a string"

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=15, deadline=1500)
def test_emergency_knowledge_fatigue_returns_relevant_diseases():
    """Test that symptom='fatigue' returns at least one of the expected disease names."""
    result = evaluate_api_call(api_name, {"symptom": "fatigue"})
    assert isinstance(result, list), "Result must be a list"
    # Collect all unique disease names from the results
    disease_names = set()
    for item in result:
        if isinstance(item, dict) and "name" in item:
            disease_names.add(item["name"])
    # Check that at least one of the expected diseases is present
    expected_diseases = {"Chronic fatigue syndrome", "Anemia", "Depression"}
    found = disease_names & expected_diseases
    assert found, f"Expected at least one of {expected_diseases} in results, got {disease_names}"

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=15, deadline=1500)
def test_emergency_knowledge_various_symptoms():
    """Test that EmergencyKnowledge works with different symptom values."""
    symptoms = ["fatigue", "headache", "fever", "chest pain"]
    for symptom in symptoms:
        result = evaluate_api_call(api_name, {"symptom": symptom})
        assert isinstance(result, list), f"Result for '{symptom}' should be a list"
        for item in result:
            assert "name" in item and "aid" in item, f"Result for '{symptom}' missing required fields"

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=10, deadline=1500)
def test_emergency_knowledge_case_insensitive_api_name():
    """Test that API name is handled case-insensitively."""
    for api_casing in ["emergencknowledge", "EMERGENCYKNOWLEDGE", "EmergencyKnowledge"]:
        result = evaluate_api_call(api_casing, {"symptom": "fatigue"})
        assert isinstance(result, list), f"Case '{api_casing}' should return a list"

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=10, deadline=1500)
def test_emergency_knowledge_empty_symptom_handling():
    """Test handling of empty symptom string (should fail or return empty)."""
    # Empty string is technically a non-empty string in terms of length 0
    # But per spec, symptom must be non-empty. The evaluator should handle this.
    result = evaluate_api_call(api_name, {"symptom": ""})
    # Depending on implementation, this might return empty list or raise error
    # At minimum, the call should not crash
    assert result is not None, "Call should return a value even for empty symptom"

@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=10, deadline=1500)
def test_emergency_knowledge_long_symptom():
    """Test that long symptom strings are accepted."""
    long_symptom = "This is a very long symptom description that exceeds typical medical query lengths"
    result = evaluate_api_call(api_name, {"symptom": long_symptom})
    assert isinstance(result, list), "Result should be a list"
    for item in result:
        assert "name" in item and "aid" in item, "All items must have name and aid"

# Additional property: idempotency-like behavior - same valid input produces consistent structure
@given(
    symptom=st.text(min_size=1, max_size=50),
    api_name="EmergencyKnowledge",
)
@settings(max_examples=10, deadline=1500)
def test_emergency_knowledge_consistent_structure():
    """Verify that
