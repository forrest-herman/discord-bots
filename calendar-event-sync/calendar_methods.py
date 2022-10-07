import json
import os

# https://github.com/forrest-herman/python-packages-common/tree/main/google_calendar_integrations
from google_calendar_integrations.gcal_methods import GoogleCalendarAccount
from google_calendar_integrations import cal_utils


def get_todays_calendar_events():
    # get all calendar events for the current day
    today_start, today_end = cal_utils.get_today_timerange()

    try:
        # prepare file paths
        client_secret_location = 'credentials/gcal_client_secret.json'
        CREDENTIALS_FILE = os.path.join(
            os.path.dirname(__file__), client_secret_location)
        token_location = 'credentials/token.pickle'
        TOKEN_FILE = os.path.join(os.path.dirname(__file__), token_location)

        # create a Google Calendar API service object
        cal = GoogleCalendarAccount(CREDENTIALS_FILE, TOKEN_FILE)
        events_from_all_calendars = cal.get_all_events(
            # maxResults=10,
            timeMin=today_start,
            timeMax=today_end,
            singleEvents=True,
            orderBy='startTime',
            timeZone='America/Toronto'
        )
    except Exception as e:
        print("Error with GCal API", e)

    events_today_info = [
        {
            'summary': get_summary_if_possible(event),  # cal_utils.get_summary_if_possible(event),
            'calendar': event['calendar'],
            'start': cal_utils.get_datetime_from_event(event['start']),
            # basically: event['end']['dateTime'] or event['end']['date']
            'end': cal_utils.get_datetime_from_event(event['end'])
        } for event in events_from_all_calendars
    ]
    events_today_info.sort(key=lambda x: x['start'])
    return events_today_info


# util functions

def get_summary_if_possible(event):
    try:
        return event['summary']
    except KeyError:
        return "No Summary"


def format_events_to_string(events_list):
    events_str_formatted = "\n".join(
        (f"{event['summary']}" + format_time(event)
         ) for event in events_list
    )
    return events_str_formatted


def format_time(event):
    if cal_utils.is_all_day(event):
        return ""
    start_end = " ({} - {})".format(
        event['start'].strftime("%#I:%M %p"),
        event['end'].strftime("%#I:%M %p")
    )
    return start_end


# testing
# print(format_events_to_string(get_todays_calendar_events()))
