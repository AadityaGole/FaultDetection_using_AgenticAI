from evaluation.api_bank_evaluator import evaluate_api_bank

# Test 1: Successful GetUserToken call with correct parameters
result1 = evaluate_api_call("GetUserToken(username='JaneSmith', password='password')")
assert result1["parsed_api_name"] == "GetUserToken"
assert result1["api_match"] is True
assert result1["params_match"] is True
assert result1["passed"] is True

# Test 2: Successful QueryAlarm call with correct parameters (March 20th, 2023 at 6:30AM)
result2 = evaluate_api_call("QueryAlarm(token='test_token', time='2023-03-20 06:30:00')")
assert result2["parsed_api_name"] == "QueryAlarm"
assert result2["api_match"] is True
assert result2["params_match"] is True
assert result2["passed"] is True

# Test 3: Case-insensitive API name matching (getusertoken -> GetUserToken)
result3 = evaluate_api_call("getusertoken(username='JaneSmith', password='password')")
assert result3["parsed_api_name"] == "GetUserToken"
assert result3["api_match"] is True

# Test 4: Missing required parameter (password) should fail
result4 = evaluate_api_call("GetUserToken(username='JaneSmith')")
assert result4["api_match"] is False
assert result4["params_match"] is False

# Test 5: Invalid date format (February 30th is invalid) should fail
result5 = evaluate_api_call("QueryAlarm(token='test_token', time='2023-02-30 06:30:00')")
assert result5["api_match"] is False
assert result5["params_match"] is False

# Test 6: Wrong API name should fail
result6 = evaluate_api_call("WrongAPI(username='JaneSmith', password='password')")
assert result6["api_match"] is False
assert result6["params_match"] is False

# Test 7: Empty parameters should fail
result7 = evaluate_api_call("GetUserToken()")
assert result7["api_match"] is False
assert result7["params_match"] is False

# Test 8: Extra unrecognized parameter should not cause failure (only required ones checked)
result8 = evaluate_api_call("GetUserToken(username='JaneSmith', password='password', role='admin')")
assert result8["api_match"] is True
assert result8["params_match"] is True
