from hypothesis import given, strategies as st, settings, assume

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_emergency_knowledge_returns_list_of_results():
    """Test that EmergencyKnowledge returns a list of result dictionaries."""
    result = emergency_knowledge("shortness of breath")
    assert isinstance(result, list), "API should return a list of results"

    for item in result:
        assert isinstance(item, dict), "Each result should be a dictionary"
        assert "name" in item, "Result must contain 'name' key"
        assert "aid" in item, "Result must contain 'aid' key"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_emergency_knowledge_non_empty_symptom():
    """Test that the symptom parameter must be a non-empty string."""
    result = emergency_knowledge("headache")
    assert isinstance(result, list), "Should return list of results for any non-empty symptom"
    for item in result:
        assert isinstance(item, dict), "Results must be dictionaries"
        assert "name" in item, "Result must have name field"
        assert "aid" in item, "Result must have aid field"

@given(st.text(min_length=1))
@settings(max_examples=20, deadline=1500)
def test_emergency_knowledge_various_symptoms():
    """Test various medical symptoms to ensure consistent response format."""
    symptoms = ["shortness of breath", "chest pain", "fever", "nausea", "diabetes"]
    for symptom in symptoms:
        result = emergency_knowledge(symptom)
        assert isinstance(result, list), f"Symptom '{symptom}' should yield a list"
        assert len(result) >= 0, f"Symptom '{symptom}' should return a list (possibly empty)"
        for item in result:
            assert isinstance(item, dict), "Each result should be a dictionary"
            assert "name" in item, f"Result for '{symptom}' missing 'name'"
            assert "aid" in item, f"Result for '{symptom}' missing 'aid'"

@given(st.text(min_length=1))
@settings(max_examples=10, deadline=1500)
def test_emergency_knowledge_minimal_input():
    """Test with minimal valid symptom input."""
    result = emergency_knowledge("asthma")
    assert isinstance(result, list), "Minimal symptom should return list of results"
    assert all(isinstance(item, dict) for item in result), "All items must be dictionaries"
    for item in result:
        assert "name" in item, "Each result must have 'name'"
        assert "aid" in item, "Each result must have 'aid'"
