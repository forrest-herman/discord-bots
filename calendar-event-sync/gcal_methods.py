import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# helpful tutorial: https://www.youtube.com/watch?v=j1mh0or2CX8
# ressources: https://developers.google.com/calendar/api/v3/reference#Freebusy

# If modifying these scopes, delete the file token.pickle
CREDENTIALS_FILE_REL = 'credentials/gcal_client_secret.json'
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), CREDENTIALS_FILE_REL)
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarAccount:
    """Defines a Google Calendar Account with service authentication"""

    def __init__(self, api_creds_path='gcal_client_secret.json', token_creds_path="token",):
        self.api_credentials = api_creds_path
        self.token_path = token_creds_path
        self.service = self.get_calendar_service()

    def get_calendar_service(self):
        # authorise user
        # https://developers.google.com/calendar/api/guides/auth
        creds = None

        ########### FIXXXXXXXXXXXXX
        filename = f'D:/PC Files/Documents/GitHub/Python/discord-bots/calendar-event-sync/credentials/{self.token_path}.pickle'
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

    def get_calendar_list(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            # for calendar_list_entry in calendar_list['items']:
            #     print(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        return calendar_list

    def get_calendar_events(self, calendarId='primary', **kwargs):
        # https://developers.google.com/calendar/api/v3/reference/events/list
        # service = get_calendar_service()
        events = self.service.events().list(calendarId=calendarId, **kwargs).execute()
        return events

    def get_all_events(self, **kwargs):
        """Returns all events in all calendars"""
        calendar_list = self.get_calendar_list()
        events = []
        for calendar_list_entry in calendar_list['items']:
            cal_events_response = self.get_calendar_events(
                calendarId=calendar_list_entry['id'], **kwargs)
            cal_name = cal_events_response['summary']
            cal_events = cal_events_response['items']

            # add the calendar name to each event dict
            result = [dict(item, calendar=cal_name) for item in cal_events]
            events.extend(result)
        return events