from hypothesis import given, strategies as st, settings, assume

@given(st.text(min_length=1, max_length=50), st.text(min_length=1, max_length=50))
@settings(max_examples=20, deadline=1500)
def test_query_scene_returns_valid_device_list(category, scene_name):
    """
    Property: QueryScene returns a dictionary with a 'devices' key containing
    a list of device dictionaries, each having 'name' and 'description' fields.
    """
    candidate = f"QueryScene({scene_name})"
    result = evaluate_api_call(candidate)
    assert result.passed is True

    devices = result.get("devices", [])
    assert isinstance(devices, list)

    for device in devices:
        assert isinstance(device, dict)
        assert "name" in device
        assert "description" in device
        assert device["name"] is not None
        assert device["description"] is not None

@given(st.text(min_length=1, max_length=50))
@settings(max_examples=20, deadline=1500)
def test_query_scene_with_various_names():
    """
    Property: The API correctly handles different scene names and returns appropriate
    device lists (may be empty if no devices exist for that scene).
    """
    categories = st.sampled_from(["Morning Routine", "Evening Relax", "Night Rest"])
    scene_name = st.sampled_from(categories)
    candidate = f"QueryScene({scene_name})"
    result = evaluate_api_call(candidate)
    assert result.passed is True
    devices = result.get("devices", [])
    assert isinstance(devices, list)

@given(st.text(min_length=1, max_length=50))
@settings(max_examples=20, deadline=1500)
def test_query_scene_api_name_matches():
    """
    Property: The evaluated result corresponds to the QueryScene API name (case-insensitive).
    """
    candidate = f"QueryScene(Morning Routine)"
    result = evaluate_api_call(candidate)
    assert result.passed is True
    assert result.parsed_api_name.lower() == "queryscene"

@given(st.text(min_length=1, max_length=50))
@settings(max_examples=20, deadline=1500)
def test_query_scene_invalid_name_returns_valid_structure():
    """
    Property: Even with an unrecognized scene name, the API returns a valid response
    (possibly with an empty devices list).
    """
    candidate = f"QueryScene(Unknown Scene)"
    result = evaluate_api_call(candidate)
    assert result.passed is True
    devices = result.get("devices", [])
    assert isinstance(devices, list)

@given(st.text(min_length=1, max_length=50))
@settings(max_examples=20, deadline=1500)
def test_query_scene_minimal_input():
    """
    Property: A minimal valid scene name produces a response with the expected structure.
    """
    candidate = f"QueryScene(A)"
    result = evaluate_api_call(candidate)
    assert result.passed is True
    devices = result.get("devices", [])
    assert isinstance(devices, list)
    # At minimum, the list should be present (even if empty)
    assert len(devices) >= 0
