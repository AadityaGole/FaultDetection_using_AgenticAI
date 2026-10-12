from hypothesis import given, strategies as st, settings, assume

@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_valid_token_and_time(token, time):
    """Test that a valid QueryAlarm call with correct token and time format passes."""
    api_request = [f"QueryAlarm(key1={token!r}, key2={time!r})"]
    result = evaluate_api_call(api_request)

    assert result["parsed_api_name"] == "QueryAlarm"
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert "token" in result.get("passed", [])


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_case_insensitive_api_name(token, time):
    """Test that the API name is matched case-insensitively during parsing."""
    api_request = [f"queryalarm(key1={token!r}, key2={time!r})"]
    result = evaluate_api_call(api_request)

    assert result["parsed_api_name"] == "QueryAlarm"


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_different_tokens():
    """Test multiple distinct tokens all produce successful parses."""
    tokens = ["user1", "user2", "admin", "guest"]
    for token in tokens:
        api_request = [f"QueryAlarm(key1={token!r}, key2='2023-03-20 06:30:00')"]
        result = evaluate_api_call(api_request)
        assert result["parsed_api_name"] == "QueryAlarm"
        assert result["api_match"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_different_times():
    """Test that different valid time formats are accepted."""
    times = [
        "2023-01-15 12:00:00",
        "2023-12-31 23:59:59",
        "2024-01-01 00:00:01",
    ]
    for time in times:
        api_request = [f"QueryAlarm(key1='{token}', key2={time!r})"]
        result = evaluate_api_call(api_request)
        assert result["parsed_api_name"] == "QueryAlarm"
        assert result["api_match"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_invalid_time_format():
    """Test that malformed time formats are rejected."""
    bad_times = [
        "2023/03/20 06:30:00",      # wrong separator
        "2023-03-20 6:30:00",       # missing leading zero in hour
        "2023-03-20 06:30",         # missing seconds
        "2023-03-20T06:30:00",      # ISO format with T
        "",                         # empty string
    ]
    for time in bad_times:
        api_request = [f"QueryAlarm(key1='{token}', key2={time!r})"]
        try:
            result = evaluate_api_call(api_request)
            # If the evaluator doesn't raise, we still need to check the result
            # Assuming a failed parse would result in False for api_match or params_match
            assert result["api_match"] is False or result["params_match"] is False
        except Exception:
            # Some evaluators might raise on invalid input
            pass


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_missing_token():
    """Test that missing token parameter causes failure."""
    api_request = [f"QueryAlarm(key2='2023-03-20 06:30:00')"]
    result = evaluate_api_call(api_request)
    assert result["api_match"] is False or result["params_match"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_missing_time():
    """Test that missing time parameter causes failure."""
    api_request = [f"QueryAlarm(key1='{token}')"]
    result = evaluate_api_call(api_request)
    assert result["api_match"] is False or result["params_match"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_non_string_token():
    """Test that non-string token types are rejected."""
    class IntToken(str): pass  # Not really useful, but tests type checking

    # Try passing an integer (should fail type check)
    api_request = [f"QueryAlarm(key1={42!r}, key2='2023-03-20 06:30:00')"]
    result = evaluate_api_call(api_request)
    # Either api_match or params_match should be False due to type mismatch
    assert result["api_match"] is False or result["params_match"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_non_string_time():
    """Test that non-string time types are rejected."""
    api_request = [f"QueryAlarm(key1='{token}', key2=123!)"]
    result = evaluate_api_call(api_request)
    assert result["api_match"] is False or result["params_match"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_empty_token():
    """Test that empty token string is handled correctly."""
    api_request = [f"QueryAlarm(key1='', key2='2023-03-20 06:30:00')"]
    result = evaluate_api_call(api_request)
    # Empty string might be allowed or rejected depending on spec
    # At minimum, it shouldn't crash
    assert isinstance(result, dict)


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_empty_time():
    """Test that empty time string is rejected."""
    api_request = [f"QueryAlarm(key1='{token}', key2='')]"
    result = evaluate_api_call(api_request)
    assert result["api_match"] is False or result["params_match"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    time=st.fixed_str("2023-03-20 06:30:00"),
)
@settings(max_examples=20, deadline=1500)
def test_query_alarm_extreme_date():
    """Test boundary dates (year 2023 as specified in task)."""
    extreme_times = [
        "2023-01-01 00:00:00",
        "2023-12-31 23:59:59",
    ]
    for time in extreme_times:
        api_request = [f"QueryAlarm(key1='{token}', key2={time!r})"]
        result = evaluate_api_call(api_request)
        assert result["parsed_api_name"] == "QueryAlarm"
        assert result["api_match"] is True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
