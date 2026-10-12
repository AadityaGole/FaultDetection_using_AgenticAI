from hypothesis import given, strategies as st, settings, assume

ALLOWED_CHARS = set("0123456789+-*/() ")

@given(st.text(min_size=1, max_size=50))
@settings(max_examples=20, deadline=1500)
def test_calculator_formula_precondition_and_postcondition(value):
    """
    Test that valid formulas produce float results.
    Encodes the precondition using assume: non-empty and only allowed characters.
    """
    formula = value.strip()
    # Precondition: formula must be non-empty and contain only digits, whitespace,
    # operators (+, -, *, /, parentheses).
    assume(len(formula) > 0, "Formula must be non-empty")
    assume(all(c in ALLOWED_CHARS for c in formula), "Formula must contain only allowed characters")

    result = api_call(formula=formula)
    # Postcondition: API returns a float equal to the evaluated formula.
    assert isinstance(result, float), f"Expected float result, got {type(result)}"

@given(st.text(min_size=1, max_size=50))
@settings(max_examples=20, deadline=1500)
def test_calculator_returns_float_for_various_formulas(value):
    """
    Verify the API consistently returns float values for different valid formulas.
    """
    result = api_call(formula=value)
    assert isinstance(result, float), f"Expected float result, got {type(result)}"
