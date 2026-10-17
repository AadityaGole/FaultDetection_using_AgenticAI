from evaluate_api_call import evaluate_api_call

def test_calculator_main_path():
    """Test the main success path: calculating (5+6)*3."""
    result = evaluate_api_call()
    assert result.passed is True

def test_calculator_invalid_expression():
    """Test that an invalid expression fails validation."""
    result = evaluate_api_call()
    assert result.passed is False
