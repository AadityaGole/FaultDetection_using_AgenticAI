def test_generated_api_call_matches_task_ground_truth():
    result = evaluate_api_call()
    assert result.parsed_api_name is not None
    assert result.parsed_api_name.lower() == 'querystock'
    assert result.api_match is True
    assert result.params_match is True
    assert result.passed is True

def test_evaluator_rejects_unparseable_output():
    result = evaluate_api_call(candidate='not an API call')
    assert result.passed is False
    assert result.parsed_api_name is None

def test_evaluator_rejects_wrong_api_name():
    result = evaluate_api_call(candidate=_wrong_api_call)
    assert result.api_match is False
    assert result.passed is False

def test_evaluator_api_name_comparison_is_case_insensitive():
    candidate = _expected_api_call.replace(_api_bank_turn.expected_api_name, _api_bank_turn.expected_api_name.swapcase(), 1)
    result = evaluate_api_call(candidate=candidate)
    assert result.api_match is True

def test_evaluator_rejects_wrong_parameters():
    result = evaluate_api_call(candidate=_wrong_params_call)
    assert result.api_match is True
    assert result.params_match is False
    assert result.passed is False
