from evaluate.api_bank_evaluator import evaluate_api_bank

# The ground truth from the task context
_expected_api_name = "ModifyRegistration"
_expected_param_dict = {
    "appointment_id": "34567890",
    "new_appointment_date": "2023-03-26",
    "new_appointment_doctor": "Dr. Lee"
}

def evaluate_api_call(candidate=None):
    """Wrapper that calls the actual evaluator."""
    return evaluate_api_bank(_api_bank_turn, candidate) if candidate is not None else evaluate_api_bank(_api_bank_turn)

def test_modify_registration_success():
    """Test successful ModifyRegistration API call with correct parameters."""
    # Correct call with proper parameters
    candidate = "[ModifyRegistration(key1='34567890', key2='2023-03-26', key3='Dr. Lee')]"
    result = evaluate_api_call(candidate)
    # The evaluator should return True for a valid call
    assert result == True, f"Expected True for valid ModifyRegistration call, got {result}"

def test_modify_registration_wrong_api_name():
    """Test that a different API name fails validation."""
    candidate = "[QueryHealthData(key1='test', key2='2023-01-01')]"
    result = evaluate_api_call(candidate)
    # Should fail because QueryHealthData is not ModifyRegistration
    assert result == False, f"Expected False for wrong API name, got {result}"

def test_modify_registration_missing_appointment_id():
    """Test that missing required appointment_id parameter causes failure."""
    candidate = "[ModifyRegistration(key2='2023-03-26', key3='Dr. Lee')]"
    result = evaluate_api_call(candidate)
    assert result == False, f"Expected False for missing appointment_id, got {result}"

def test_modify_registration_missing_new_date():
    """Test that missing new_appointment_date parameter causes failure."""
    candidate = "[ModifyRegistration(key1='34567890', key3='Dr. Lee')]"
    result = evaluate_api_call(candidate)
    assert result == False, f"Expected False for missing new_appointment_date, got {result}"

def test_modify_registration_missing_new_doctor():
    """Test that missing new_appointment_doctor parameter causes failure."""
    candidate = "[ModifyRegistration(key1='34567890', key2='2023-03-26')]"
    result = evaluate_api_call(candidate)
    assert result == False, f"Expected False for missing new_appointment_doctor, got {result}"

def test_modify_registration_invalid_date_format():
    """Test that an invalid date format (not YYYY-MM-DD) fails."""
    candidate = "[ModifyRegistration(key1='34567890', key2='2023-13-45', key3='Dr. Lee')]"
    result = evaluate_api_call(candidate)
    assert result == False, f"Expected False for invalid date format, got {result}"

def test_modify_registration_different_case_api_name():
    """Test that case-insensitive API name matching works (e.g., MODIFYREGISTRATION)."""
    candidate = "[MODIFYREGISTRATION(key1='34567890', key2='2023-03-26', key3='Dr. Lee')]"
    result = evaluate_api_call(candidate)
    # The evaluator should treat this as a match due to case-insensitive comparison
    assert result == True, f"Expected True for case-insensitive API name match, got {result}"

def test_modify_registration_whitespace_variations():
    """Test that whitespace variations in the call string still parse correctly."""
    # Extra spaces around keys/values
    candidate = "[ ModifyRegistration (key1='34567890', key2='2023-03-26', key3='Dr. Lee') ]"
    result = evaluate_api_call(candidate)
    assert result == True, f"Expected True for whitespace-variation call, got {result}"

def test_cancel_registration_success():
    """Test successful CancelRegistration call."""
    candidate = "[CancelRegistration(key1='abc123')]"
    result = evaluate_api_call(candidate)
    assert result == True, f"Expected True for valid CancelRegistration call, got {result}"

def test_cancel_registration_wrong_api_name():
    """Test that calling CancelRegistration when expecting ModifyRegistration fails."""
    candidate = "[CancelRegistration(key1='abc123')]"
    result = evaluate_api_call(candidate)
    assert result == False, f"Expected False for wrong API name, got {result}"

def test_cancel_registration_missing_appointment_id():
    """Test that missing appointment_id in CancelRegistration fails."""
    candidate = "[CancelRegistration(key2='2023-01-01')]"
    result = evaluate_api_call(candidate)
    assert result == False, f"Expected False for missing appointment_id, got {result}"
