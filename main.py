from __future__ import print_function

import datetime
import os.path
from rich import print
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Read + Write Authorization
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():

    creds = None
    
    # Load credentials from json
    FROM = json.load(open("calendarrules/rules.json"))["FROM"]
    TO = json.load(open("calendarrules/rules.json"))["TO"]

    if os.path.exists('calendarrules/token.json'):
        creds = Credentials.from_authorized_user_file('calendarrules/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'calendarrules/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('calendarrules/token.json', 'w') as token:
            token.write(creds.to_json())


    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId=FROM, 
            timeMin=now, 
            singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return

        for event in events:
            title = event['summary'].lower()
            if ("albe" in title or "alberto" in title) and  "/" in title:
                # print(event)
                service.events().insert(calendarId=TO, body=event).execute()
        
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()