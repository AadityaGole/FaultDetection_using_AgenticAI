from evaluate.api_bank_evaluator import evaluate_api_call


def test_query_scene_main_path():
    """Main test: verify the QueryScene API call with Morning Routine scene name passes evaluation."""
    result = evaluate_api_call()
    assert result.passed is True


def test_query_scene_correct_format():
    """Verify the API request format matches the expected pattern [QueryScene(name='Morning Routine
