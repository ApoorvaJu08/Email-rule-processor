import unittest
from unittest.mock import MagicMock, patch
from process_emails import apply_rules, check_condition, perform_actions, string_to_integer, get_date_difference
from datetime import datetime


class TestStringToInteger(unittest.TestCase):
    def test_valid_input(self):
        self.assertEqual(string_to_integer("123"), 123)
    
    def test_invalid_input(self):
        self.assertIsNone(string_to_integer("abc"))
        self.assertIsNone(string_to_integer("12.3"))
        self.assertIsNone(string_to_integer("1,000"))
        self.assertIsNone(string_to_integer(""))
    
    def test_zero_input(self):
        self.assertEqual(string_to_integer("0"), 0)
    
    def test_positive_integer(self):
        self.assertEqual(string_to_integer("+123"), 123)
    
    def test_negative_integer(self):
        self.assertEqual(string_to_integer("-123"), -123)
    
    def test_large_integer(self):
        self.assertEqual(string_to_integer("12345678901234567890"), 12345678901234567890)
    
    def test_large_negative_integer(self):
        self.assertEqual(string_to_integer("-12345678901234567890"), -12345678901234567890)


class TestGetDateDifference(unittest.TestCase):
    def test_days_difference(self):
        given_date = '2024-03-15'
        expected_difference = 9
        self.assertEqual(get_date_difference(given_date, unit='days'), expected_difference)

    def test_months_difference(self):
        given_date = '2024-01-01'
        expected_difference = 2
        self.assertEqual(get_date_difference(given_date, unit='months'), expected_difference)



class TestApplyRules(unittest.TestCase):
    def test_apply_rules_all_true(self):
        # Mock rules
        rules = {
            'rules': [
                {
                    'predicate': 'All', 
                    'conditions': [
                        {'field': 'subject', 'value': 'Test', 'predicate': 'Contains'}, 
                        {'field': 'sender', 'value': 'sender@example.com', 'predicate': 'Equals'}
                    ],
                    'actions': ['Mark as read']
                }
            ]
        }

        # Mock email
        email = {'subject': 'Test', 'sender': 'sender@example.com'}

        # Call the function
        perform_actions_mock = MagicMock()
        with patch('process_emails.perform_actions', perform_actions_mock):
            apply_rules(email, rules)

        # Assertions
        perform_actions_mock.assert_called_once_with(email, ['Mark as read'])

    def test_apply_rules_any_true(self):
        # Mock rules
        rules = {
            'rules': [
                {
                    'predicate': 'Any', 
                    'conditions': [
                        {'field': 'subject', 'value': 'Test', 'predicate': 'Contains'}, 
                        {'field': 'sender', 'value': 'sender@example.com', 'predicate': 'Equals'}
                    ], 
                    'actions': ['Mark as read']
                }
            ]
        }

        # Mock email
        email = {'subject': 'Test2', 'sender': 'sender@example.com'}

        # Call the function
        perform_actions_mock = MagicMock()
        with patch('process_emails.perform_actions', perform_actions_mock):
            apply_rules(email, rules)

        # Assertions
        perform_actions_mock.assert_called_once_with(email, ['Mark as read'])
