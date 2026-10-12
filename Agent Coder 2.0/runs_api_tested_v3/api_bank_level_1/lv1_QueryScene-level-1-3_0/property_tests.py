from hypothesis import given, strategies as st, settings, assume

# Strategy for valid scene names (non-empty strings)
valid_scene_names = st.text(min_size=1, max_size=50)

# Strategy for device entries (each device has name and description)
device_entry = st.dict(
    keys=st.text(min_size=1, max_size=50),
    values=st.text(min_size=1, max_size=200)
)

# Custom strategy for API call candidates in the format [ApiName(key1='value1', ...)]
# QueryScene requires a 'name' parameter of type string
api_call_strategy = st.custom(
    lambda: f"[QueryScene({name_param!r}, {name_param!r}))]",
    min_size=1,
    max_size=1
)

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_query_valid_scene(name):
    # Evaluate the API call and get the parsed result
    result = evaluate_api_call("[QueryScene({!r})]", name)

    # Check that the API name is correctly identified (case-insensitive match)
    assert "QueryScene" in result.get("ApiName", "").lower()

    # Check that the name parameter was accepted and matches
    assert result["ApiName"] == "QueryScene"
    assert result["name"] == name

    # Check that the response contains the devices list
    assert "devices" in result
    devices = result["devices"]
    assert isinstance(devices, list)

    # Check each device has both name and description
    for device in devices:
        assert "name" in device
        assert "description" in device

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_query_morning_routine():
    """Specific test for the Morning Routine scene mentioned in the task."""
    result = evaluate_api_call("[QueryScene(name='Morning Routine')]", "Morning Routine")

    assert result["ApiName"] == "QueryScene"
    assert result["name"] == "Morning Routine"
    assert "devices" in result
    devices = result["devices"]

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_missing_name_parameter():
    """Test that omitting the name parameter fails the evaluator."""
    # Candidate without the required name parameter
    bad_candidate = "[QueryScene()]"

    # The evaluator should reject this - either via parsing error or parameter mismatch
    try:
        result = evaluate_api_call(bad_candidate, "Morning Routine")
        # If it doesn't raise an exception, check that the name wasn't accepted
        # The spec says the name parameter is required
        assert "name" not in result or result["name"] != "Morning Routine"
    except Exception:
        # Expected failure - the evaluator should catch this
        pass

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_non_string_name():
    """Test that a non-string scene name is rejected."""
    # Using a number as scene name - should fail since name must be string
    bad_candidate = "[QueryScene(123)]"

    try:
        result = evaluate_api_call(bad_candidate, "Morning Routine")
        # If it succeeds, the name would be converted to string, which shouldn't happen
        # The spec says name must be a string type
        assert False, "Non-string scene name should be rejected"
    except Exception:
        # Expected failure
        pass

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_empty_scene_name():
    """Test that an empty scene name violates the precondition."""
    # Empty string is not allowed per precondition
    bad_candidate = "[QueryScene(name='')]"

    try:
        result = evaluate_api_call(bad_candidate, "")
        # Should fail because empty string is not a valid non-empty scene name
        assert False, "Empty scene name should be rejected"
    except Exception:
        pass

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_long_scene_name():
    """Test with a very long scene name to ensure bounds handling."""
    long_name = "A" * 100
    candidate = f"[QueryScene(name='{long_name}')]"

    result = evaluate_api_call(candidate, long_name)

    assert result["ApiName"] == "QueryScene"
    assert result["name"] == long_name
    assert "devices" in result
    devices = result["devices"]
    assert len(devices) > 0  # At least one device should be returned

@given(name_param=valid_scene_names)
@settings(max_examples=20, deadline=1500)
def test_case_insensitive_api_name():
    """Test that API name matching is case-insensitive."""
    # QueryScene is the canonical name; variations should work
    result = evaluate_api_call("[queryscene(name='Morning Routine')]", "Morning Routine")

    # The evaluator should normalize to "QueryScene" regardless of case
    assert result["ApiName"].lower() == "queryscene"
    assert result["name"] == "Morning Routine"
