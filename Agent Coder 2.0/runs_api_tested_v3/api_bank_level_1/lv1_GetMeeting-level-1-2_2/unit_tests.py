import pytest
from evaluate.api_bank_evaluator import evaluate_api_bank

# Ground truth from the task
EXPECTED_API_NAME = "QueryMeeting"
EXPECTED_PARAM_DICT = {
    "token": "a9s8d7f6g5h4j3k2l1",
    "meeting_topic": "Sales Meeting",
    "start_time": "2023-03-20 14:00:00",
    "end_time": "2023-03-20 16:00:00",
    "location": "Conference Room A",
    "attendees": []
}

def _generate_valid_api_call():
    """Helper to generate the expected valid API call string."""
    return "[QueryMeeting(token='a9s8d7f6g5h4j3k2l1', meeting_topic='Sales Meeting', start_time='2023-03-20 14:00:00', end_time='2023-03-20 16:00:00', location='Conference Room A', attendees=[])]"

def _generate_invalid_api_call_wrong_name():
    """Generate an API call with wrong API name."""
    return "[PaymentsAPI(amount=100)]"

def _generate_invalid_api_call_missing_params():
    """Generate an API call with missing required parameters."""
    return "[QueryMeeting(meeting_topic='Test
