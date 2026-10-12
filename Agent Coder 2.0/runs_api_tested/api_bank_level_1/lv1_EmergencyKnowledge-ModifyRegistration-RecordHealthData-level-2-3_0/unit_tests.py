from api_call import api_call

def test_api_call_shortness_of_breath():
    """Test the main success path: query for shortness of breath."""
    result = api_call(symptom='shortness of breath')
    expected = "[ApiName(symptom='shortness of breath')]"
    assert result == expected

def test_api_call_empty_symptom():
    """Edge case: empty symptom string should still produce a valid API call."""
    result = api_call(symptom='')
    assert isinstance(result, str)
    assert "ApiName" in result

def test_api_call_none_symptom():
    """Edge case: None symptom should be handled gracefully."""
    result = api_call(symptom=None)
    assert isinstance(result, str)
    # Even with None, the API call string should be valid
    assert "ApiName" in result

def test_api_call_invalid_type_symptom():
    """Edge case: non-string symptom type should still produce a call (though may fail later)."""
    result = api_call(symptom=123)
    assert isinstance(result, str)
    # The API call format should still be generated even with wrong type
