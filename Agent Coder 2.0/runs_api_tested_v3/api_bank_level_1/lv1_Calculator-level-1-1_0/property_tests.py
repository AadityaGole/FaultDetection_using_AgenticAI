from hypothesis import given, strategies as st, settings, assume

# Assuming the evaluator function is available in the environment
# We'll import it from the local module if needed
# from my_module import evaluate_api_call

def evaluate_api_call(candidate):
    """Mock implementation for demonstration - replace with actual import."""
    # In reality, this would call the actual evaluator
    # For now, we simulate the expected behavior
    try:
        # Parse the candidate string to extract api_name and formula
        # Expected format: "[ApiName(key1='value1', key2='value2', ...)]"
        # But evaluate_api_call likely receives structured data
        # Based on the task description, it takes an API call with api_name and formula
        # Let's assume it accepts (api_name, formula) tuple or dict

        # Since we don't have the real function, we'll define a simple version
        # that mimics the expected behavior described in the spec
        import re

        # Extract api_name (first word inside brackets)
        match = re.match(r'\[(.*?)\]', candidate)
        if not match:
            raise ValueError("Invalid API call format")

        api_name = match.group(1).strip()

        # Check if api_name matches 'Calculator' case-insensitively
        if api_name.lower() != 'calculator':
            raise ValueError(f"API name must be 'Calculator' (case-insensitive), got '{api_name}'")

        # Extract formula parameter
        # Look for formula key-value pair
        formula_match = re.search(r'"formula"\s*:\s*"([^"]*)"', candidate)
        if not formula_match:
            raise ValueError("Missing 'formula' parameter")

        formula = formula_match.group(1)

        # Validate formula contains only allowed characters
        allowed_chars = set('0123456789+-*/().
