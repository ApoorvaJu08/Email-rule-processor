## Built using

- Python 3.10


## Installation

- Clone the repository to your local machine:

- git clone https://github.com/ApoorvaJu08/Email-rule-processor.git

- Navigate to the project directory:

    - create the virtual environment: python -m venv venv

    - activate the virtual environment by: source venv/bin/activate

    - Install the required Python packages:

        - pip install -r requirements.txt


## Usage

1. Authentication to Gmail API

Before running the script, you need to set up OAuth 2.0 authentication credentials for accessing the Gmail API. Follow these steps:

    Go to the Google Cloud Console.
    Create a new project (if you haven't already).
    Enable the Gmail API for your project.
    Create OAuth 2.0 credentials (OAuth client ID) for a desktop application.
    Download the credentials JSON file and save it as credentials.json in the project directory.

2. Run the Script

To run the script, execute the following command:

    - python fetch_emails.py

The script will fetch emails from your Gmail inbox, store them in a SQLite3 database (emails.db), and process them based on rules specified in email_rules.json.

3. Specify Rules

Define the rules for processing emails in the email_rules.json file. Each rule should include conditions (field name, predicate, value) and actions to be performed if the conditions are met.

4. Customize Actions

Customize the actions performed on emails based on rule conditions in the script's perform_actions() function.

5. Apply the rules

    - python process_emails.py


## Database Schema

The SQLite3 database schema includes a single table named emails with the following columns:

    id (INTEGER, PRIMARY KEY): Unique identifier for each email.
    sender (TEXT): Email address of the sender.
    receiver (TEXT): Email address of the receiver
    subject (TEXT): Subject line of the email.
    received_date (TEXT): Date and time when the email was received.
    read: (BOOL): Marks the email as read if True otherwise False
    folder (TEXT): Name of the folder where email resides