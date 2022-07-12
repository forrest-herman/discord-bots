import datetime
import os
import pickle

import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# helpful tutorial: https://www.youtube.com/watch?v=j1mh0or2CX8
# ressources: https://developers.google.com/calendar/api/v3/reference#Freebusy

# If modifying these scopes, delete the file token.pickle
CREDENTIALS_FILE = 'D:/PC Files/Documents/GitHub/Python/discord-bots/calendar-event-sync/credentials/gcal_client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

NUM_USERS = 1


def get_calendar_service():
    # authorise user
    # https://developers.google.com/calendar/api/guides/auth
    creds = None

    filename = 'D:/PC Files/Documents/GitHub/Python/discord-bots/calendar-event-sync/credentials/token.pickle'
    # The file token.pickle stores the user's tokens, and is created automatically
    #  when the authorization flow completes for the first time.
    if os.path.exists(filename):
        with open(filename, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # print('credentials refreshed')
            except Exception as e:
                print(e)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES)
            creds = flow.run_local_server(port=50547)

            # Save the credentials for the next run
            with open(filename, 'wb') as token:
                pickle.dump(creds, token)

    # generate the service object using the credentials
    service = build('calendar', 'v3', credentials=creds)
    return service


def get_calendar_list():
    # service = get_calendar_service()

    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        # for calendar_list_entry in calendar_list['items']:
        #     print(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendar_list


def get_calendar_events(calendarId='primary', **kwargs):
    # https://developers.google.com/calendar/api/v3/reference/events/list
    # service = get_calendar_service()
    events = service.events().list(calendarId=calendarId, **kwargs).execute()
    return events


# get events from all calendars
def get_all_events(**kwargs):
    calendar_list = get_calendar_list()
    events = []
    for calendar_list_entry in calendar_list['items']:
        cal_events_response = get_calendar_events(calendarId=calendar_list_entry['id'], **kwargs)
        cal_name = cal_events_response['summary']
        cal_events = cal_events_response['items']

        # add the calendar name to each event dict
        result = [dict(item, calendar=cal_name) for item in cal_events]
        events.extend(result)
    return events


# main functions
service = get_calendar_service()
