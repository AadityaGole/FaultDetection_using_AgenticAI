from hypothesis import given, strategies as st, settings, assume

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed_str("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_valid_call(token, content, time, location):
    """Test that a valid AddAgenda call with all required parameters succeeds."""
    args = {
        "token": token,
        "content": content,
        "time": time,
        "location": location
    }
    result = evaluate_api_call("AddAgenda", args)
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed_str("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    args = {
        "token": token,
        "content": content,
        "time": time,
        "location": location
    }
    result = evaluate_api_call("ADDAGENDA", args)
    # The evaluator should still recognize this as AddAgenda despite case difference
    assert result["api_match"] is True

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed_str("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_empty_content_fails():
    """Test that empty content parameter causes failure."""
    args = {
        "token": token,
        "content": "",
        "time": time,
        "location": location
    }
    result = evaluate_api_call("AddAgenda", args)
    assert result["passed"] is False

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed_str("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_missing_token_fails():
    """Test that missing token parameter causes failure."""
    args = {
        "token": "",  # intentionally empty/invalid
        "content": content,
        "time": time,
        "location": location
    }
    result = evaluate_api_call("AddAgenda", args)
    assert result["passed"] is False

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed_str("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_invalid_time_format_fails():
    """Test that invalid time format causes failure."""
    # Try various invalid formats
    invalid_times = [
        "2023-12-15 14",      # missing seconds
        "2023-12-15 24:00:00", # invalid hour
        "2023-12-15 14:60:00", # invalid minute
        "2023-12-15 25:00:00", # invalid hour
        "2023-12-15 12:00",    # missing seconds
        "2023-12-15T14:00:00", # ISO format instead of space
    ]
    for time in invalid_times:
        args = {
            "token": token,
            "content": content,
            "time": time,
            "location": location
        }
        result = evaluate_api_call("AddAgenda", args)
        assert result["passed"] is False

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed_str("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_whitespace_wrapping():
    """Test that whitespace-wrapped calls preserve parsed API name and parameters."""
    args = {
        "token": token,
        "content": content,
        "time": time,
        "location": location
    }
    # Add extra whitespace around values (should be preserved/normalized)
    wrapped_args = {k: v.strip() for k, v in args.items()}
    result = evaluate_api_call("AddAgenda", wrapped_args)
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True
