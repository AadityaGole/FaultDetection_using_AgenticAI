from hypothesis import given, strategies as st, settings, assume

@given(
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=20, deadline=1500)
def test_add_agenda_valid_call(token, content, time, location):
    call_str = f"[AddAgenda](token='{token}', content='{content}', time='{time}', location='{location}')"
    result = evaluate_api_call(call_str)

    assert result["parsed_api_name"] == "AddAgenda"
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

@given(
    api_name=st.sampled_from(["addagenda", "ADDAGENDA", "AddAgenda", "addagenda"]),
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=10, deadline=1500)
def test_case_insensitive_api_name(api_name, token, content, time, location):
    call_str = f"[{api_name}](token='{token}', content='{content}', time='{time}', location='{location}')"
    result = evaluate_api_call(call_str)

    assert result["parsed_api_name"] == "AddAgenda"
    assert result["api_match"] is True
    assert result["params_match"] is True
    assert result["passed"] is True

@given(
    api_name=st.sampled_from(["addagenda", "ADDAGENDA", "AddAgenda"]),
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00"),
    location=st.text(min_size=1)
)
@settings(max_examples=10, deadline=1500)
def test_missing_required_parameters(api_name, token, content, time, location):
    # Omit one required parameter to trigger param mismatch
    call_str = f"[{api_name}](token='{token}', content='{content}', time='{time}')"
    result = evaluate_api_call(call_str)

    # Should fail because location is missing
    assert result["api_match"] is False
    assert result["params_match"] is False

@given(
    api_name=st.sampled_from(["addagenda", "ADDAGENDA", "AddAgenda"]),
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00")
)
@settings(max_examples=10, deadline=1500)
def test_empty_location():
    call_str = f"[AddAgenda](token='{token}', content='{content}', time='{time}', location='')"
    result = evaluate_api_call(call_str)

    # Should fail because location is empty
    assert result["api_match"] is True
    assert result["params_match"] is False

@given(
    api_name=st.sampled_from(["addagenda", "ADDAGENDA", "AddAgenda"]),
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00")
)
@settings(max_examples=10, deadline=1500)
def test_invalid_time_format():
    call_str = f"[AddAgenda](token='{token}', content='{content}', time='invalid-time', location='somewhere')"
    result = evaluate_api_call(call_str)

    # Should fail due to invalid time format
    assert result["api_match"] is True
    assert result["params_match"] is False

@given(
    api_name=st.sampled_from(["addagenda", "ADDAGENDA", "AddAgenda"]),
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00")
)
@settings(max_examples=10, deadline=1500)
def test_non_string_location():
    call_str = f"[AddAgenda](token='{token}', content='{content}', time='{time}', location=123)"
    result = evaluate_api_call(call_str)

    # Should fail because location is not a string
    assert result["api_match"] is True
    assert result["params_match"] is False

@given(
    api_name=st.sampled_from(["addagenda", "ADDAGENDA", "AddAgenda"]),
    token=st.text(min_size=1),
    content=st.text(min_size=1),
    time=st.fixed("2023-12-15 14:00:00")
)
@settings(max_examples=10, deadline=1500)
def test_non_string_content():
    call_str = f"[AddAgenda](token='{token}', content='{content}', time='{time}', location='meeting')"
    result = evaluate_api_call(call_str)

    # Should fail because content is not a string (if evaluator enforces this)
    assert result["api_match"] is True
    assert result["params_match"] is False
