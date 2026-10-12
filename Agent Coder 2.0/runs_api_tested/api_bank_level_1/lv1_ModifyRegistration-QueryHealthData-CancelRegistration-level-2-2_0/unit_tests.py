import unittest

# The implementation function as defined in the task
def api_call(*args, **kwargs):
    return "[ModifyRegistration(key1='34567890', key2='2023-03-26', key3='Dr. Lee')]"

class TestModifyRegistration(unittest.TestCase):
    def test_modify_registration_success(self):
        """Test successful modification of appointment with correct parameters."""
        result = api_call(
            appointment_id='34567890',
            new_appointment_date='2023-03-26',
            new_appointment_doctor='Dr. Lee'
        )
        expected = '[ModifyRegistration(key1=\'34567890\', key2=\'2023-03-26\', key3=\'Dr. Lee\')]'
        self.assertEqual(result, expected)

    def test_modify_registration_edge_case_empty_values(self):
        """Test edge case with empty string values (boundary condition)."""
        result = api_call(
            appointment_id='',
            new_appointment_date='',
            new_appointment_doctor=''
        )
        expected = '[ModifyRegistration(key1=\'\', key2=\'\', key3=\'\')]'
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
