from evaluate.api_bank_evaluator import evaluate_api_call

def test_successful_queryalarm_evaluation():
    """Test successful QueryAlarm API call evaluation."""
    result = evaluate_api_call()

    # Check API name is correctly identified (case-insensitive match)
    assert result["parsed_api_name"] == "QueryAlarm"

    # Check token parameter matches expected value
    assert result["params_match"]["token"] == "o8i7u6y5t4r3e2w1q0"

    # Check time parameter matches expected format
    assert result["params_match"]["time"] == "2023-03-20 06:30:00"

def test_missing_required_token():
    """Test that missing token parameter causes evaluation to fail."""
    result = evaluate_api_call("[QueryAlarm(time='2023-03-20 06:30:00
