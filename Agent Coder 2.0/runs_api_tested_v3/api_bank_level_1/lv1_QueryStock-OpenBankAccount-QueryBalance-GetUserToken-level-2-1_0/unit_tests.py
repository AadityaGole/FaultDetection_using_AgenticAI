from evaluate.api_bank_evaluator import evaluate_api_bank

def evaluate_api_call(candidate=None):
    """Wrapper that calls the API evaluator with the given candidate."""
    return evaluate_api_call(candidate)

# Ground truth from the task:
# Expected API name: "QueryStock"
# Expected param dict: {"stock_code": "AMZN", "date": "2022-03-12"}

# Test 1: Main success path - correct QueryStock call with proper parameters
result1 = evaluate_api_call("[ApiName(key1='AMZN', key2='2022-03-12
