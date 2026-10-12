from evaluate.api_bank_evaluator import evaluate_api_bank
from dataset.api_bank_loader import APIBankTurn

# Reconstruct the turn object as defined in the implementation
api_turn_json = {
    "task_id": "lv1_EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3",
    "level": 1,
    "dialogue_id": "EmergencyKnowledge-ModifyRegistration-RecordHealthData-level-2-3",
    "turn_id": 0,
    "api_descriptions": """\nGenerate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] based on the previous dialogue context.\nThe current year is 2023.\nInput: \nUser: User's utterence\nAI: AI's response\n\nExpected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\nAPI descriptions:\n{\"name\": \"EmergencyKnowledge\", \"description\": \"This API searches for a given symptom for emergency knowledge.\", \"input_parameters\": {\"symptom\": {\"type\": \"str\", \"description\": \"The symptom to search.\"}}, \"output_parameters\": {\"results\": {\"type\": \"list\", \"description\": \"The list of results. Format be like [{\\"name\\":possible disease name, \\"aid\\": first-aid method},...]\"}}}\n{\"name\": \"RecordHealthData\", \"description\": \"This API records the health data of a user.\", \"input_parameters\": {\"user_id\": {\"type\": \"str\", \"description\": \"The ID of user.\"}, \"time\": {\"type\": \"str\", \"description\": \"The time of health data. Format: %Y-%m-%d %H:%M:%S\"}, \"health_data\": {\"type\": \"list\", \"description\": \"The health data, with the format like [{\'name\': \"blood_pressure\", \"value\": \"120/80\"}, {\'name\': \"heart_rate\", \"value\": \"80\"}]\"}}, \"output_parameters\": {\"status\": {\"type\": \"str\", \"description\": \"The status of recording.\"}}}\n{\"name\": \"ModifyRegistration\", \"description\": \"This API modifies the registration of a patient given appointment ID.\", \"input_parameters\": {\"appointment_id\": {\"type\": \"str\", \"description\": \"The ID of appointment.\"}, \"new_appointment_date\": {\"type\": \"str\", \"description\": \"The new appointment date. Format: %Y-%m-%d.\"}, \"new_appointment_doctor\": {\"type\": \"str\", \"description\": \"The new appointment doctor.\"}}, \"output_parameters\": {\"status\": {\"type\": \"str\", \"description\": \"The status of modification.\"}}}""",
    "expected_api_name": "EmergencyKnowledge",
    "expected_param_dict": {"symptom": "shortness of breath"},
    "prompt": "Generate an API request in the format of [ApiName(key1='value1', key2='value2', ...)] based on the previous dialogue context.\nThe current year is 2023.\nInput: \nUser: User's utterence\nAI: AI's response\n\nExpected output:\nAPI-Request: [ApiName(key1='value1', key2='value2', ...)]\n\nAPI descriptions:\n..."}
}

_api_bank_turn = APIBankTurn(**json.loads(api_turn_json))

def evaluate_api_call(candidate=None):
    """Wrapper around the actual implementation."""
    output = api_call() if candidate is None else candidate
    return evaluate_api_bank(_api_bank_turn, output)

def api_call():
    """Generates the expected API call string."""
    return "[ApiName(symptom='shortness of breath
