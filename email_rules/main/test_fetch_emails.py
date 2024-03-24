import unittest
from unittest.mock import MagicMock
from fetch_emails import convert_date_to_YMD, extract_message_headers, extract_message_body
from datetime import datetime


class TestConvertDateToYMD(unittest.TestCase):
    def test_convert_date_to_YMD(self):
        date_str = "Tue, 01 Jan 2024 12:00:00 +0000"
        expected_date = "2024-01-01"
        self.assertEqual(convert_date_to_YMD(date_str), expected_date)

class TestExtractMessageHeaders(unittest.TestCase):
    def test_extract_message_headers(self):
        msg = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'receiver@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Tue, 01 Jan 2024 12:00:00 +0000'}
                ]
            }
        }
        sender, receiver, subject, received_date = extract_message_headers(msg)
        self.assertEqual(sender, 'sender@example.com')
        self.assertEqual(receiver, 'receiver@example.com')
        self.assertEqual(subject, 'Test Subject')
        self.assertEqual(received_date, '2024-01-01')

class TestExtractMessageBody(unittest.TestCase):
    def test_extract_message_body(self):
        # Case 1: Text/plain part present
        msg1 = {
            'payload': {
                'parts': [
                    {'mimeType': 'text/plain', 'body': {'data': 'Test Body'}}
                ]
            }
        }
        self.assertEqual(extract_message_body(msg1), 'Test Body')
        
        # Case 2: Text/plain part absent, fallback to payload body
        msg2 = {
            'payload': {
                'body': {'data': 'Test Body from Payload'}
            }
        }
        self.assertEqual(extract_message_body(msg2), 'Test Body from Payload')
