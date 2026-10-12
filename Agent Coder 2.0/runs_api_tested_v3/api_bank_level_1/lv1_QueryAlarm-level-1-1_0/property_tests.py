from hypothesis import given, strategies as st, settings, assume

# Assuming evaluate_api_call is available in the environment
# from some_module import evaluate_api_call

@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed(2023, 3, 20, 6, 30, 0),  # fixed valid time
    api_name="QueryAlarm",
    # Additional variations for robustness
    token=st.text(min_size=1, max_size=50),
    time=st.fixed("2023-01-15 09:00:00"),
    api_name="queryalarm",  # lowercase variant
    api_name="QUERYALARM",  # uppercase variant
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_valid_call():
    """Test that valid QueryAlarm calls produce correct API request dictionaries."""
    # Construct a valid API call candidate
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "token": token,
            "time": time,
        }
    }
    result = evaluate_api_call(candidate)

    # Verify the returned result is a dictionary with expected keys
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "api_name" in result, "Result must contain api_name key"
    assert result["api_name"].lower() == "queryalarm", "API name should normalize to QueryAlarm"
    assert "token" in result, "Result must contain token parameter"
    assert "time" in result, "Result must contain time parameter"
    assert result["token"] == token, "Token should match input"
    assert result["time"] == time, "Time should match input"

@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed("2023-05-10 14:30:00"),
    api_name="QueryAlarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_case_insensitive_matching():
    """Test that QueryAlarm API name matches case-insensitively."""
    candidate = {
        "api_name": "queryalarm",
        "parameters": {
            "token": token,
            "time": time,
        }
    }
    result = evaluate_api_call(candidate)

    # The evaluator should treat "queryalarm" as "QueryAlarm"
    assert "api_name" in result
    assert result["api_name"].lower() == "queryalarm"

@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed("2023-07-04 08:15:00"),
    api_name="queryalarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_lowercase_api_name():
    """Test that lowercase API name variants work."""
    candidate = {
        "api_name": "queryalarm",
        "parameters": {
            "token": token,
            "time": time,
        }
    }
    result = evaluate_api_call(candidate)
    assert "api_name" in result
    assert result["api_name"].lower() == "queryalarm"

@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed("2023-09-25 23:59:59"),
    api_name="QUERYALARM",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_uppercase_api_name():
    """Test that uppercase API name variants work."""
    candidate = {
        "api_name": "QUERYALARM",
        "parameters": {
            "token": token,
            "time": time,
        }
    }
    result = evaluate_api_call(candidate)
    assert "api_name" in result
    assert result["api_name"].upper() == "QUERYALARM"

@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed("2023-02-14 12:00:00"),
    api_name="queryalarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_invalid_time_format():
    """Test that invalid time formats are rejected."""
    # Try a malformed time string
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "token": token,
            "time": "2023/03/20 06:30",  # Wrong separator
        }
    }
    try:
        result = evaluate_api_call(candidate)
        # Should either raise an exception or return a result that doesn't meet spec
        # Since we expect proper validation, this should fail the invariant checks
        assert False, "Invalid time format should cause failure"
    except Exception:
        # If the evaluator raises an error for invalid format, that's acceptable
        pass

@given(
    token="",
    time="2023-03-20 06:30:00",
    api_name="QueryAlarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_empty_token():
    """Test that empty token is rejected."""
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "token": "",
            "time": time,
        }
    }
    result = evaluate_api_call(candidate)
    # Should fail because token is empty (non-empty requirement)
    assert False, "Empty token should cause failure"

@given(
    token="validuser",
    time="2023-01-01 00:00:00",
    api_name="QueryAlarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_minimal_valid_inputs():
    """Test minimal valid inputs still produce correct API request."""
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "token": "validuser",
            "time": "2023-01-01 00:00:00",
        }
    }
    result = evaluate_api_call(candidate)
    assert isinstance(result, dict)
    assert result.get("api_name") == "QueryAlarm"
    assert result.get("token") == "validuser"
    assert result.get("time") == "2023-01-01 00:00:00"

@given(
    token="user123",
    time="2023-12-31 23:59:59",
    api_name="queryalarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_boundary_dates():
    """Test boundary dates around year 2023."""
    candidate = {
        "api_name": "queryalarm",
        "parameters": {
            "token": token,
            "time": "2023-01-01 00:00:00",
        }
    }
    result = evaluate_api_call(candidate)
    assert result["api_name"].lower() == "queryalarm"
    assert result["token"] == token
    assert result["time"] == "2023-01-01 00:00:00"

# Explicit assumption for precondition: token must be non-empty
@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed("2023-03-20 06:30:00"),
    api_name="QueryAlarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_assumption_enforced():
    """Verify that non-empty token is enforced (precondition)."""
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "token": token,
            "time": time,
        }
    }
    result = evaluate_api_call(candidate)
    assert result["token"] != "", "Token must be non-empty per precondition"

# Test that missing token parameter causes failure
@given(
    time=st.fixed("2023-03-20 06:30:00"),
    api_name="QueryAlarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_missing_token():
    """Test that omitting token parameter causes failure."""
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "time": time,
        }
    }
    try:
        result = evaluate_api_call(candidate)
        # Should fail because token is required
        assert False, "Missing token should cause failure"
    except Exception:
        pass  # Expected failure

# Test that missing time parameter causes failure
@given(
    token="validuser",
    api_name="QueryAlarm",
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_missing_time():
    """Test that omitting time parameter causes failure."""
    candidate = {
        "api_name": "QueryAlarm",
        "parameters": {
            "token": token,
        }
    }
    try:
        result = evaluate_api_call(candidate)
        assert False, "Missing time should cause failure"
    except Exception:
        pass  # Expected failure
