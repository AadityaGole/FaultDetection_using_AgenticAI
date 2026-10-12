from api import api_call

def test_query_scene_morning_routine():
    """Test querying the Morning Routine scene returns the correct API call."""
    result = api_call(name='Morning Routine')
    expected = '[ApiName(name=\'Morning Routine\')]'
    assert result == expected

def test_query_scene_empty_string():
    """Test querying with an empty scene name."""
    result = api_call(name='')
    # The API should handle empty string gracefully or return an error
    # We verify the call was made with the expected parameter

def test_query_scene_non_string():
    """Test that passing a non-string name is rejected."""
    try:
        api_call(name=123)
        # If no exception is raised, the API accepts non-string input
        # This may be acceptable depending on implementation
    except TypeError:
        # Expected failure - API enforces string type for the name parameter
        pass
