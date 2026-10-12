from hypothesis import given, strategies as st, settings, assume

@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-03-20 14:00:00"),
    end_time=st.fixed_str("2023-03-20 16:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=10),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_valid_params(call):
    """Test that valid QueryMeeting API calls pass the evaluator."""
    result = evaluate_api_call(call)
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-05-15 09:30:00"),
    end_time=st.fixed_str("2023-05-15 11:30:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=5),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_date_format():
    """Test that dates in correct YYYY-MM-DD HH:MM:SS format pass."""
    call = {
        "token": "valid_token",
        "meeting_topic": "Team Sync",
        "start_time": "2023-07-01 08:00:00",
        "end_time": "2023-07-01 17:00:00",
        "location": "Conference Room B",
        "attendees": ["Alice", "Bob"],
    }
    result = evaluate_api_call(call)
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-06-10 13:00:00"),
    end_time=st.fixed_str("2023-06-10 15:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=3),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_min_length_constraints():
    """Test that parameters respect minimum length constraints."""
    call = {
        "token": "tok",
        "meeting_topic": "A",  # Exactly 1 char (< 50)
        "start_time": "2023-04-01 12:00:00",
        "end_time": "2023-04-01 14:00:00",
        "location": "Room X",  # Exactly 100 chars would be too long, so keep shorter
        "attendees": ["User1"],
    }
    result = evaluate_api_call(call)
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-09-25 10:00:00"),
    end_time=st.fixed_str("2023-09-25 12:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=4),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_max_length_constraints():
    """Test that parameters respect maximum length constraints."""
    call = {
        "token": "token_abc",
        "meeting_topic": "ShortTopic",  # Under 50 chars
        "start_time": "2023-10-01 09:00:00",
        "end_time": "2023-10-01 17:00:00",
        "location": "LargeLocationName",  # Under 100 chars
        "attendees": ["Alice", "Bob", "Charlie"],  # 3 attendees
    }
    result = evaluate_api_call(call)
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-02-14 14:30:00"),
    end_time=st.fixed_str("2023-02-14 16:30:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=6),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    call = {
        "token": "token_xyz",
        "meeting_topic": "CaseTest",
        "start_time": "2023-03-01 10:00:00",
        "end_time": "2023-03-01 12:00:00",
        "location": "Conference Hall",
        "attendees": ["AttendeeOne"],
    }
    result = evaluate_api_call(call)
    # Should still pass even though "QueryMeeting" != "querymeeting" exactly
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-05-05 08:00:00"),
    end_time=st.fixed_str("2023-05-05 18:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=8),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_invalid_meeting_topic_length():
    """Test that meeting_topic exceeding 50 chars fails."""
    call = {
        "token": "token_1",
        "meeting_topic": "A" * 51,  # 52 characters > 50
        "start_time": "2023-06-01 09:00:00",
        "end_time": "2023-06-01 17:00:00",
        "location": "Room Y",
        "attendees": ["User"],
    }
    result = evaluate_api_call(call)
    # Should fail - params_match should be False
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is False
    assert result["api_call"]["passed"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-07-01 12:00:00"),
    end_time=st.fixed_str("2023-07-01 14:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=3),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_missing_parameter():
    """Test that missing required parameters causes failure."""
    call = {
        "token": "token_ok",
        "meeting_topic": "Meeting",
        # Missing start_time, end_time, location, attendees
    }
    result = evaluate_api_call(call)
    # Should fail - params_match should be False
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is False
    assert result["api_call"]["passed"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-08-01 09:00:00"),
    end_time=st.fixed_str("2023-08-01 11:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=2),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_non_string_attendee():
    """Test that non-string attendees cause failure."""
    call = {
        "token": "token_ok",
        "meeting_topic": "Test",
        "start_time": "2023-09-01 10:00:00",
        "end_time": "2023-09-01 12:00:00",
        "location": "Room Z",
        "attendees": [123]  # Not a string
    }
    result = evaluate_api_call(call)
    # Should fail - params_match should be False
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is False
    assert result["api_call"]["passed"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-10-01 13:00:00"),
    end_time=st.fixed_str("2023-10-01 15:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=5),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_empty_attendees_list():
    """Test that empty attendees list passes (it's a valid list of strings)."""
    call = {
        "token": "token_ok",
        "meeting_topic": "EmptyAttendees",
        "start_time": "2023-11-01 09:00:00",
        "end_time": "2023-11-01 17:00:00",
        "location": "Conference Room C",
        "attendees": [],  # Empty list is valid
    }
    result = evaluate_api_call(call)
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-12-01 14:00:00"),
    end_time=st.fixed_str("2023-12-01 16:00:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=4),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_long_location():
    """Test that location respects 100 character limit."""
    call = {
        "token": "token_ok",
        "meeting_topic": "LongTopic",
        "start_time": "2023-12-02 10:00:00",
        "end_time": "2023-12-02 12:00:00",
        "location": "A" * 101,  # 102 characters > 100
        "attendees": ["User"],
    }
    result = evaluate_api_call(call)
    # Should fail - params_match should be False
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is False
    assert result["api_call"]["passed"] is False


@given(
    token=st.text(min_size=1, max_size=50),
    meeting_topic=st.text(max_size=50),
    start_time=st.fixed_str("2023-01-15 09:30:00"),
    end_time=st.fixed_str("2023-01-15 11:30:00"),
    location=st.text(max_size=100),
    attendees=st.lists(st.text(min_size=1, max_size=20), max_size=6),
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_duplicate_attendee_names():
    """Test that duplicate attendee names are allowed (no uniqueness constraint)."""
    call = {
        "token": "token_dup",
        "meeting_topic": "Duplicates",
        "start_time": "2023-01-16 08:00:00",
        "end_time": "2023-01-16 10:00:00",
        "location": "Hall D",
        "attendees": ["Alice", "Alice"],  # Duplicate names - should be allowed
    }
    result = evaluate_api_call(call)
    assert result["api_call"]["api_name"] == "QueryMeeting"
    assert result["api_call"]["api_match"] is True
    assert result["api_call"]["params_match"] is True
    assert result["api_call"]["passed"] is True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
