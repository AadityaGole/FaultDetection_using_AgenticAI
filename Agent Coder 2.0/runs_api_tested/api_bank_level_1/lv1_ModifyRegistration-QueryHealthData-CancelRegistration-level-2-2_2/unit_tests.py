from unittest import TestCase

class TestAPICall(TestCase):
    def test_modify_registration_success(self):
        """Test ModifyRegistration with all required parameters."""
        result = api_call(
            appointment_id='34567890',
            new_appointment_date='2023-03-26',
            new_appointment_doctor='Dr. Lee'
        )
        expected = "[ModifyRegistration(appointment_id='34567890', new_appointment_date='2023-03-26', new_appointment_doctor='Dr. Lee')]->success"
        self.assertEqual(result, expected)

    def test_query_health_data_success(self):
        """Test QueryHealthData with all required parameters."""
        result = api_call(
            user_id='J46801',
            start_time='2023-03-05 00:00:00',
            end_time='2023-03-12 23:59:59'
        )
        expected = "[QueryHealthData(user_id='J46801', start_time='2023-03-05 00:00:00', end_time='2023-03-12 23:59:59')]"
        self.assertEqual(result, expected)

    def test_modify_registration_missing_doctor(self):
        """Test ModifyRegistration with missing required parameter (doctor)."""
        result = api_call(
            appointment_id='34567890',
            new_appointment_date='2023-03-26'
        )
        # The call is constructed but validation occurs downstream
        self.assertIn('ModifyRegistration', result)

    def test_query_health_data_empty_user_id(self):
        """Test QueryHealthData with empty user_id."""
        result = api_call(
            user_id='',
            start_time='2023-03-05 00:00:00',
            end_time='2023-03-12 23:59:59'
        )
        expected = "[QueryHealthData(user_id='', start_time='2023-03-05 00:00:00', end_time='2023-03-12 23:59:59')]"
        self.assertEqual(result, expected)
