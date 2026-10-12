from hypothesis import given, strategies as st, settings, assume

# Strategy for valid API call strings for QueryMeeting
# Includes base API name variants, token, meeting_topic, fixed timestamps,
# location within 100 chars, and attendees list of 2+ strings

@given(
    # Case-insensitive API name variants
    st.sampled_from(['QueryMeeting', 'querymeeting', 'QUERYMEETING']),
    # Token string (non-empty)
    st.text(min_size=1, max_size=50),
    # Meeting topic
    st.text(min_size=1, max_size=50),
    # Start time - fixed per specification
    st.fixed_str('2023-03-20 14:00:00'),
    # End time - fixed per specification
    st.fixed_str('2023-03-20 16:00:00'),
    # Location up to 100 characters
    st.text(max_size=100),
    # Attendees list of exactly 2 strings (as per expected output)
    st.lists(
        st.text(min_size=1, max_size=30), min_size=2, max_size=5
    )
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_valid_call():
    """
    Test that a valid QueryMeeting API call produces a correctly parsed and validated result.
    Verifies API name matching (case-insensitive), presence of all required parameters,
    and correct values for the specific meeting instance.
    """
    candidate = (
        f"QueryMeeting token={candidate_token} "
        f"meeting_topic={candidate_topic} "
        f"start_time={candidate_start} "
        f"end_time={candidate_end} "
        f"location={candidate_location} "
        f"attendees={candidate_attendees}"
    )

    result = evaluate_api_call(candidate=candidate)

    # Result must be a list with an ApiName object
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) >= 1, "Expected non-empty result list"

    api_request = result[0]
    assert 'ApiName' in api_request, "Missing ApiName in result"
    assert api_request['ApiName'].get('key1') == 'QueryMeeting', \
        f"API name mismatch: expected 'QueryMeeting', got '{api_request.get('ApiName',{}).get('key1')}'"

    # Verify all required parameters are present
    required_params = ['token', 'meeting_topic', 'start_time', 'end_time', 'location', 'attendees']
    for param in required_params:
        assert param in api_request, f"Missing required parameter: {param}"

    # Verify parameter types and values for this specific instance
    assert api_request['token'] == 'str', "token should be string"
    assert api_request['meeting_topic'] == 'Sales Meeting', \
        f"meeting_topic mismatch: expected 'Sales Meeting', got '{api_request.get('meeting_topic')}'"
    assert api_request['start_time'] == '2023-03-20 14:00:00', \
        f"start_time mismatch: expected '2023-03-20 14:00:00', got '{api_request.get('start_time')}'"
    assert api_request['end_time'] == '2023-03-20 16:00:00', \
        f"end_time mismatch: expected '2023-03-20 16:00:00', got '{api_request.get('end_time')}'"
    assert api_request['location'] == 'Conference Room A', \
        f"location mismatch: expected 'Conference Room A', got '{api_request.get('location')}'"
    assert api_request['attendees'] == ['John Smith', 'Jane Doe'], \
        f"attendees mismatch: expected ['John Smith', 'Jane Doe'], got {api_request.get('attendees')}"

# Test case-insensitive API name handling
@given(
    st.sampled_from(['QueryMeeting', 'querymeeting', 'QUERYMEETING']),
    st.text(min_size=1, max_size=50),
    st.fixed_str('2023-03-20 14:00:00'),
    st.fixed_str('2023-03-20 16:00:00'),
    st.text(max_size=100),
    st.lists(st.text(min_size=1, max_size=30), min_size=2, max_size=5)
)
@settings(max_examples=20, deadline=1500)
def test_query_meeting_case_insensitive():
    """
    Test that the evaluator accepts QueryMeeting regardless of case variation.
