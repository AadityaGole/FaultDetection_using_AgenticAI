from hypothesis import given, strategies as st, settings

@given(prefix=st.text(alphabet=' \t\r\n', max_size=8), suffix=st.text(alphabet=' \t\r\n', max_size=8))
@settings(max_examples=20, deadline=1500)
def test_evaluator_result_is_invariant_to_surrounding_whitespace(prefix, suffix):
    baseline = evaluate_api_call()
    transformed = evaluate_api_call(candidate=prefix + api_call() + suffix)
    assert transformed.passed is baseline.passed
    assert transformed.api_match is baseline.api_match
    assert transformed.params_match is baseline.params_match

@given(prefix=st.text(alphabet=' \t\r\n', max_size=8), suffix=st.text(alphabet=' \t\r\n', max_size=8))
@settings(max_examples=20, deadline=1500)
def test_expected_call_passes_with_surrounding_whitespace(prefix, suffix):
    result = evaluate_api_call(candidate=prefix + _expected_api_call + suffix)
    assert result.api_match is True
    assert result.params_match is True
    assert result.passed is True
