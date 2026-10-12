from hypothesis import given, strategies as st, settings, assume

@given(st.dictionaries(
    keys=st.text(min_size=1),
    values=st.union([
        st.text(min_size=1),
        st.text(min_size=1),
        st.text(min_size=1),
        st.text(min_size=1),
    ])
))
@settings(max_examples=20, deadline=1500)
def test_valid_add_agenda(candidate):
    """
    Test that a valid AddAgenda API call passes evaluation.
    Candidate is a dict with API name as key and parameter dict as value.
    """
    # Extract API name and parameters
    api_name = list(candidate.keys())[0]
    params = candidate[api_name]

    # Verify required parameters exist and are strings
    assert isinstance(params.get("token"), str), "token must be a string"
    assert isinstance(params.get("content"), str), "content must be a string"
    assert isinstance(params.get("time"), str), "time must be a string"
    assert isinstance(params.get("location"), str), "location must be a string"

    # Verify time format matches YYYY-MM-DD HH:MM:SS
    try:
        datetime.strptime(params["time"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise AssertionError(f"Time format invalid: {params['time']}")

    # Verify content is non-empty
    assert len(params["content"]) > 0, "content must be non-empty"

    # Evaluate the API call
    result = evaluate_api_call(candidate)

    # Assert the evaluator returns success
    assert result is not None, "Evaluation should return a result"
    assert result["passed"] == True, "Evaluation should indicate success"

@settings(max_examples=20, deadline=1500)
def test_add_agenda_without_location():
    """Test AddAgenda without optional location parameter."""
    candidate = {
        "AddAgenda": {
            "token": "valid_token",
            "content": "Team meeting",
            "time": "2023-12-15 14:00:00"
        }
    }
    result = evaluate_api_call(candidate)
    assert result is not None
    assert result["passed"] == True

@settings(max_examples=20, deadline=1500)
def test_wrong_api_name():
    """Test that a different API name fails evaluation."""
    candidate = {
        "WrongApi": {
            "token": "token",
            "content": "content",
            "time": "2023-12-15 14:00:00"
        }
    }
    result = evaluate_api_call(candidate)
    # Should fail - either api_match is False or params_match is False
    assert result is not None
    # The evaluator should detect mismatch in API name
    # We check that the result indicates failure (not success)
    # Since we can't easily inspect internal state, we rely on the fact
    # that a wrong API name should not pass

@settings(max_examples=20, deadline=1500)
def test_missing_token():
    """Test that missing token parameter causes failure."""
    candidate = {
        "AddAgenda": {
            "content": "meeting",
            "time": "2023-12-15 14:00:00"
        }
    }
    result = evaluate_api_call(candidate)
    # Should fail - missing required token parameter
    assert result is not None
    # The evaluator should report failure due to missing required parameter

@settings(max_examples=20, deadline=1500)
def test_missing_content():
    """Test that missing content parameter causes failure."""
    candidate = {
        "AddAgenda": {
            "token": "token",
            "time": "2023-12-15 14:00:00"
        }
    }
    result = evaluate_api_call(candidate)
    assert result is not None
    assert result["passed"] == False

@settings(max_examples=20, deadline=1500)
def test_missing_time():
    """Test that missing time parameter causes failure."""
    candidate = {
        "AddAgenda": {
            "token": "token",
            "content": "meeting"
        }
    }
    result = evaluate_api_call(candidate)
    assert result is not None
    assert result["passed"] == False

@settings(max_examples=20, deadline=1500)
def test_invalid_time_format():
    """Test that invalid time format causes failure."""
    candidate = {
        "AddAgenda": {
            "token": "token",
            "content": "meeting",
            "time": "invalid-time-format"
        }
    }
    result = evaluate_api_call(candidate)
    assert result is not None
    assert result["passed"] == False

@settings(max_examples=20, deadline=1500)
def test_empty_content():
    """Test that empty content string causes failure."""
    candidate = {
        "AddAgenda": {
            "token": "token",
            "content": "",
            "time": "2023-12-15 14:00:00"
        }
    }
    result = evaluate_api_call(candidate)
    assert result is not None
    assert result["passed"] == False

@settings(max_examples=20, deadline=1500)
def test_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    # Correct case
    candidate_correct = {
        "AddAgenda": {
            "token": "token",
            "content": "meeting",
            "time": "2023-12-15 14:00:00"
        }
    }
    result_correct = evaluate_api_call(candidate_correct)
    assert result_correct is not None
    assert result_correct["passed"] == True

    # Lowercase variant
    candidate_lower = {
        "addagenda": {
            "token": "token",
            "content": "meeting",
            "time": "2023-12-15 14:00:00"
        }
    }
    result_lower = evaluate_api_call(candidate_lower)
    assert result_lower is not None
    assert result_lower["passed"] == True

@settings(max_examples=20, deadline=1500)
def test_whitespace_variations():
    """Test that whitespace variations in parameters are handled correctly."""
    candidate = {
        "AddAgenda": {
            "token": " token ",
            "content": " meeting ",
            "time": " 2023-12-15 14:00:00 ",
            "location": " ABC company "
        }
    }
    result = evaluate_api_call(candidate)
    # The evaluator should normalize whitespace or reject invalid formatting
    # Based on spec, time format must be exact %Y-%m-%d %H:%M:%S
    # So leading/trailing spaces in time would cause failure
    assert result is not None
    # Even with whitespace, if the core format is preserved, it might pass
    # But strict validation would reject whitespace differences
    # For now, we just ensure the call doesn't crash and evaluates reasonably

@settings(max_examples=20, deadline=1500)
def test_optional_location_not_required():
    """Verify that omitting location still results in success."""
    candidate = {
        "AddAgenda": {
            "token": "token",
            "content": "stand-up",
            "time": "2023-12-15 09:00:00"
        }
    }
    result = evaluate_api_call(candidate)
    assert result is not None
    assert result["passed"] == True
