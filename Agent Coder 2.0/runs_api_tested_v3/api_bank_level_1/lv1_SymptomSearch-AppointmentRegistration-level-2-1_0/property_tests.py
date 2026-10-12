from hypothesis import given, strategies as st, settings, assume

# Strategy for valid symptom strings (non-empty, reasonable length)
symptom_strategy = st.text(min_size=1, max_size=50, filter=lambda s: len(s) > 0)

# Positive test: valid SymptomSearch call with symptom="fatigue"
@given(symptom=symptom_strategy)
@settings(max_examples=20, deadline=1500)
def test_valid_symptom_search_fatigue():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom="fatigue"
    )
    assert result["parsed_api_name"] == "SymptomSearch"
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert isinstance(result.get("results"), list)

# Positive test: valid SymptomSearch call with another symptom
@given(symptom=st.text(min_size=1, max_size=30))
@settings(max_examples=15, deadline=1500)
def test_valid_symptom_search_different_symptom():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom="headache"
    )
    assert result["api_match"] is True
    assert isinstance(result.get("results"), list)

# Negative test: wrong API name (should fail)
@given(api_name=st.sampled_from(["WrongAPI", "symptomsearch", "Symptomsearch", "", "appointment"]))
@settings(max_examples=10, deadline=1500)
def test_invalid_api_name():
    # The evaluator should reject non-matching API names
    result = evaluate_api_call(
        api_name=api_name,
        symptom="fatigue"
    )
    assert result["api_match"] is False

# Negative test: missing required parameter (should fail)
@given(symptom=st.text(min_size=1, max_size=50))
@settings(max_examples=10, deadline=1500)
def test_missing_symptom_parameter():
    # When symptom is not provided, the evaluator should detect the missing required param
    with pytest.raises(Exception):  # May raise ValueError, KeyError, or similar
        evaluate_api_call(
            api_name="SymptomSearch",
            # symptom intentionally omitted
        )

# Edge case: empty symptom string (violates precondition - non-empty required)
@given(symptom=st.text())
@settings(max_examples=5, deadline=1500)
def test_empty_symptom_string():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom=""  # Empty string violates precondition
    )
    assert result["api_match"] is False

# Negative test: non-string symptom type (should fail due to type mismatch)
@given(symptom=st.floats(min_value=-100, max_value=100))
@settings(max_examples=5, deadline=1500)
def test_non_string_symptom():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom=42.5  # Float instead of string
    )
    assert result["api_match"] is False

# Negative test: null/None symptom (should fail)
@given(symptom=st.none())
@settings(max_examples=5, deadline=1500)
def test_none_symptom():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom=None
    )
    assert result["api_match"] is False

# Property test: symptom parameter determines search scope (sanity check)
@given(symptom=st.text(min_size=1, max_size=40))
@settings(max_examples=15, deadline=1500)
def test_symptom_parameter_preserved():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom=symptom
    )
    # The symptom parameter should be preserved in the parsed result
    assert result["params_match"] is True
    # We cannot fully verify the internal logic without seeing the full result dict,
    # but we can check that the API name and basic structure are intact
    assert result["api_match"] is True
    assert result["parsed_api_name"] == "SymptomSearch"

# Property test: multiple valid calls should produce consistent structural patterns
@given(symptom=st.text(min_size=1, max_size=30))
@settings(max_examples=10, deadline=1500)
def test_consistent_result_structure():
    result = evaluate_api_call(
        api_name="SymptomSearch",
        symptom=symptom
    )
    assert isinstance(result, dict)
    assert "parsed_api_name" in result
    assert "api_match" in result
    assert "params_match" in result
    assert "results" in result
    if result["results"]:
        first_result = result["results"][0]
        assert "name" in first_result
        assert "description" in first_result
