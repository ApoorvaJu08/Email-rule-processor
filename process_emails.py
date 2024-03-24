import sqlite3
import json
import os.path
from datetime import datetime


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



def fetch_emails_from_database():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute("SELECT * FROM email_metadata LIMIT 10")  # Limiting to 10 emails
    email_metadatas = c.fetchall()
    emails = []
    for row in email_metadatas:
        email_id, sender, receiver, subject, received_date, read, folder = row
            
        email = {
            'id': email_id,
            'sender': sender,
            'receiver': receiver,
            'subject': subject,
            'received_date': received_date,
            'read': read,
            'folder': folder
        }
        emails.append(email)
    conn.close()
    return emails


# Step 3 & 4: Process Emails Based on Rules
def process_emails(rules):
    emails = fetch_emails_from_database()
    for email in emails:
        apply_rules(email, rules)


def apply_rules(email, rules):
    for rule in rules['rules']:
        if rule['predicate'] == 'All':
            if all(check_condition(email, condition) for condition in rule['conditions']):
                perform_actions(email, rule['actions'])
        elif rule['predicate'] == 'Any':
            if any(check_condition(email, condition) for condition in rule['conditions']):
                perform_actions(email, rule['actions'])


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


def perform_actions(email, actions):
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    for action in actions:
        if action == 'Mark as read':
            # Implement mark as read action
            email['read'] = True
        elif action == 'Mark as unread':
            # Implement mark as unread action
            email['read'] = False
        elif action.startswith('Move Message'):
            # Implement move message action
            folder_name = action.split("to")[-1].strip()
            email['folder'] = folder_name
    c.execute("UPDATE email_metadata set read = ?, folder = ? where id = ?", (email['read'], email['folder'], email['id']))
    conn.commit()
    conn.close()


def main():

    # # Step 3 & 4: Process emails based on rules
    with open('email_rules.json') as f:
        rules = json.load(f)
    process_emails(rules)
    print(fetch_emails_from_database())


if __name__ == "__main__":
    main()
