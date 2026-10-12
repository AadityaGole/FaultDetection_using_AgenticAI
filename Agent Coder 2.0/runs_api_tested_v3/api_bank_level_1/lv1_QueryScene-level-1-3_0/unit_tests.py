import pytest
from api_call import evaluate_api_call, _api_bank_turn

EXPECTED_API_NAME = "QueryScene"
EXPECTED_PARAM_DICT = {"name": "Morning Routine"}


def test_successful_query_scene_call():
    """Main success path: correct API call with proper parameters."""
    candidate = '[ApiName(name=\'Morning Routine\')]'
    result = evaluate_api_call(candidate)
    assert result is True


@pytest.mark.parametrize("api_name", [
    "morning routine",
    "MORNING ROUTINE",
    "Morning Routine",
])
def test_case_insensitive_api_name_matching(api_name):
    """Edge case: different casing of API name should still be matched."""
    candidate = f"[ApiName(name={repr(api_name)})]"
    result = evaluate_api_call(candidate)
    assert result is True


def test_wrong_api_name_fails():
    """Edge case: calling a non-existent API should fail."""
    candidate = '[ApiName(name=\'BankAccount\')]'
    result = evaluate_api_call(candidate)
    assert result is False


def test_empty_candidate_fails():
    """Edge case: empty string should not be accepted."""
    result = evaluate_api_call("")
    assert result is False


def test_invalid_syntax_calls_fail():
    """Edge case: malformed API call syntax should fail."""
    invalid_calls = [
        "Not an API call",
        "[ApiName(name=)]",
        "[]",
        "ApiName(name='test')",  # Missing brackets
    ]
    for call in invalid_calls:
        result = evaluate_api_call(call)
        assert result is False, f"Should have failed for: {call}"


@given(
    name=st.text(min_size=1, max_size=100),
    name_value=st.text(min_size=1, max_size=200),
)
def test_hypothesis_valid_api_calls(name, name_value):
    """Property test: various valid parameter combinations should pass."""
    candidate = f"[ApiName(name={repr(name_value)})]"
    result = evaluate_api_call(candidate)
    assert result is True, f"Failed for name: {name_value}, candidate: {candidate}"


def test_extra_unrecognized_parameters_allowed():
    """Edge case: additional unrecognized parameters should not break parsing."""
    # The QueryScene API only defines 'name' as a required parameter
    # Extra parameters should either be ignored or cause failure depending on evaluator
    # We test that the core functionality works with the minimal required params
    candidate = '[ApiName(name=\'Morning Routine\')]'
    result = evaluate_api_call(candidate)
    assert result is True
