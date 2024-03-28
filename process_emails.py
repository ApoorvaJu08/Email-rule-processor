import sqlite3
import json
import os.path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from fetch_emails import extract_message_headers, extract_message_body

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Define a mapping of predicate strings to comparison functions
predicate_functions = {
    'Contains': lambda x, y: y in x,
    'Does not Contain': lambda x, y: y not in x,
    'Equals': lambda x, y: x == y,
    'Does not equal': lambda x, y: x != y,
    'Less than': lambda x, y: compare_dates(x, y, 'less'),
    'Greater than': lambda x, y: compare_dates(x, y, 'greater')
}


def string_to_integer(input_string):
    try:
        return int(input_string)
    except ValueError:
        print("Invalid input: cannot convert to integer")
        return None


def get_date_difference(date_str, unit='days'):
    # Convert the date string to a datetime object
    given_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the difference between the dates
    if unit == 'days':
        difference = (current_date - given_date).days
    elif unit == 'months':
        difference = (current_date.year - given_date.year) * 12 + current_date.month - given_date.month
    else:
        raise ValueError("Invalid unit. Must be 'days' or 'months'.")
    
    return difference


# Step 3 & 4: Process Emails Based on Rules
def process_emails(emails, rules, service):
    for email in emails:
        apply_rules(email, rules, service)


def apply_rules(email, rules, service):
    for rule in rules['rules']:
        if rule['predicate'] == 'All':
            if all(check_condition(email, condition) for condition in rule['conditions']):
                perform_actions(email, rule['actions'], service)
        elif rule['predicate'] == 'Any':
            if any(check_condition(email, condition) for condition in rule['conditions']):
                perform_actions(email, rule['actions'], service)


def compare_dates(date1, date2, comparison):
    """
    Compare two dates.
    
    Args:
        date1 (str): First date in string format.
        date2 (str): Second date in string format.
        comparison (str): 'less' or 'greater' for comparison direction.
        
    Returns:
        bool: True if date1 is less/greater than date2, otherwise False.
    """
    if 'D' in date2:
        unit = 'days'
    elif 'M' in date2:
        unit = 'months'
    else:
        return False
    
    date_diff = get_date_difference(date1, unit)
    value = int(date2.replace('D', '').replace('M', ''))
    
    if comparison == 'less':
        return date_diff < value
    elif comparison == 'greater':
        return date_diff > value
    else:
        return False


def check_condition(email, condition):
    field = condition['field']
    value = condition['value']
    
    if field not in email:
        return False
    
    predicate = condition['predicate']
    
    # Get the comparison function corresponding to the predicate
    comparison_function = predicate_functions.get(predicate)
    
    # Perform the comparison if a valid function is found
    if comparison_function:
        return comparison_function(email[field], value)
    
    return False


def perform_actions(email, actions, service):
    for action in actions:
        if action == 'Mark as read':
            mark_as_read(email, service)
        elif action == 'Mark as unread':
            mark_as_unread(email, service)
        elif action.startswith('Move Message'):
            move_message(email, action.split("to")[-1].strip(), service)

def mark_as_read(email, service):
    message_id = email['message_id']
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

def mark_as_unread(email, service):
    message_id = email['message_id']
    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()

def move_message(email, folder_name, service):
    message_id = email['message_id']
    labels = {'INBOX': 'INBOX', 'Sent': 'SENT', 'Trash': 'TRASH', 'Spam': 'SPAM'}
    label_id = labels.get(folder_name, 'INBOX')
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['INBOX', 'UNREAD'], 'addLabelIds': [label_id]}).execute()


def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=2).execute()
    messages = results.get('messages', [])
    emails = []
    if messages:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Extract message headers
            sender, receiver, subject, received_date = extract_message_headers(msg)
            
            # Extract message body
            message_body = extract_message_body(msg)

            emails.append({
                'sender': sender,
                'receiver': receiver,
                'subject': subject,
                'message_body': message_body,
                'received_date': received_date,
                'read': False,
                'folder': 'inbox',
                'message_id': message['id']
            })

    # # Step 3 & 4: Process emails based on rules
    with open('email_rules.json') as f:
        rules = json.load(f)
    process_emails(emails, rules, service)

if __name__ == "__main__":
    main()
