from hypothesis import given, strategies as st, settings

@given(name=st.text(min_size=1, max_size=50))
@settings(max_examples=20, deadline=1500)
def test_query_scene_api_call(name):
    """
    Test that the QueryScene API call includes the provided scene name.

    Precondition: name is a non-empty string (enforced by min_size=1).
    Postcondition: The API response string contains the scene name.
    """
    result = api_call(name=name)
    assert isinstance(result, str), f"Expected string response, got {type(result)}"
    assert name in result, f"Scene name '{name}' not found in API response: {result}"

@given(name=st.text(min_size=1, max_size=50))
@settings(max_examples=20, deadline=1500)
def test_various_scenes():
    """
    Test that various scene names produce API calls with those names.
    """
    for name in ("Morning Routine", "Evening Relax", "Work Day", "Night Rest"):
        result = api_call(name=name)
        assert isinstance(result, str), f"Expected string response for scene '{name}', got {type(result)}"
        assert name in result, f"Scene name '{name}' not found in API response: {result}"
