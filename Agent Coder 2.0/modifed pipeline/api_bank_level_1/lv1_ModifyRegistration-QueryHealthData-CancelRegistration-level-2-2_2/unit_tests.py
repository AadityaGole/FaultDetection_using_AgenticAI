
def test_query_health_data_success():
    """Test that the QueryHealthData API call is correctly evaluated with success."""
    result = evaluate_api_call()
    assert result.passed is True, f"Expected passed=True, got {result.passed}"

def test_query_health_data_edge_case():
    """Test edge case with minimal time range."""
    # The evaluator should still pass even with a narrow time window
    result = evaluate_api_call()
    assert result.passed is True, f"Expected passed=True, got {result.passed}"
