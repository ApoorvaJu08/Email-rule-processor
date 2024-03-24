import json
import os.path
import sqlite3
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
from dateutil import parser

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


# Step 1: Authenticate to Google's Gmail API
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def convert_date_to_YMD(date_str):
    # Parse the input date string using dateutil.parser
    parsed_date = parser.parse(date_str)
    
    # Format the date as "Y-M-D"
    formatted_date = parsed_date.strftime("%Y-%m-%d")
    
    return formatted_date



def extract_message_headers(msg):
    sender = ''
    receiver = ''
    subject = ''
    received_date = ''

    for header in msg['payload']['headers']:
        if header['name'] == 'From':
            sender = header['value']
        elif header['name'] == 'To':
            receiver = header['value']
        elif header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'Date':
            received_date = convert_date_to_YMD(header['value'])

    return sender, receiver, subject, received_date


def extract_message_body(msg):
    if 'parts' in msg['payload']:
        parts = msg['payload']['parts']
        for part in parts:
            if part['mimeType'] == 'text/plain':
                return part['body']['data']
    else:
        return msg['payload']['body']['data']


def fetch_emails():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
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
                'folder': 'inbox'
            })

    return emails


# Step 2: Store Emails in a Relational Database
def create_database():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS email_metadata
                 (id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, subject TEXT, received_date TEXT, read BOOLEAN, folder TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS email_body
                 (id INTEGER PRIMARY KEY, email_id INTEGER, message TEXT, FOREIGN KEY(email_id) REFERENCES email_metadata(id))''')
    conn.commit()
    conn.close()


def insert_email(email):
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute("INSERT INTO email_metadata (sender, receiver, subject, received_date, read, folder) VALUES (?, ?, ?, ?, ?, ?)",
              (email['sender'], email['receiver'], email['subject'], email['received_date'], email['read'], email['folder']))
    c.execute("INSERT INTO email_body (email_id, message) VALUES (?, ?)",
              (c.lastrowid, email['message_body']))
    conn.commit()
    conn.close()


def main():
    # Step 1: Fetch emails from Gmail API
    emails = fetch_emails()
    print(emails)

    # Step 2: Store emails in a database
    create_database()
    for email in emails:
        insert_email(email)


if __name__ == "__main__":
    main()
