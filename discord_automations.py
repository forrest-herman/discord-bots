import os
from datetime import datetime
from firestore_methods import set_last_updated, get_last_updated
# from calendar_event_sync.bot import *
from reading_updates.get_book_progress import get_book_progress

from discord_client import start_bot

# custom package found at:
# https://github.com/forrest-herman/python-packages-common/tree/main/google_calendar_integrations
from google_calendar_integrations.gcal_methods import GoogleCalendarAccount
from google_calendar_integrations import cal_utils

from calendar_event_sync.calendar_methods import get_todays_calendar_events

FORM_URL = os.getenv('CHECK_IN_FORM')
FORM_FREQUENCY = 2 # twice a month

# add functions for daily messages


def main():
    bot_messages = []

    """ prepare all messages into list of dicts of the type:
    {
        'messageStr': 'message',
        'channelName': 'channelName'
    }
    """

    forrest_events, angele_events = [], []
    # get the last updated date from firestore
    # discord calendar events
    # discord reading notifications
    calendar_last_updated = get_last_updated('discord_calendarEvents')
    print('calendar_last_updated', calendar_last_updated)
    
    if calendar_last_updated is None or calendar_last_updated.date() < datetime.now().date():
        # send calendar events
        events_to_exclude = ['Forrest Herman Preteckt', 'Personal old',
                             'angele.beaulne@gmail.com', 'McMaster Outlook',
                             'Recurring Reminders', 'Haddon House']

        today_events = get_todays_calendar_events()
        print('today_events', today_events)
        forrest_events = cal_utils.filter_events_by_calendar(
            today_events, events_to_exclude,
            exclude=True
        )
        angele_events = cal_utils.filter_events_by_calendar(
            today_events, ['angele.beaulne@gmail.com'])

        if today_events:
            # set the last updated date to firestore
            set_last_updated('discord_calendarEvents')


    ### Monthly Check-in Form
    # check day of month for sending the form
    form_days = [15]
    last_check_in = get_last_updated('discord_relationshipCheckIn')
    if datetime.today().day in form_days and last_check_in.date() < datetime.now().date():
        # send form
        bot_messages.append({
            'messageStr': 'How are things going? Fill out this form to find out 😊\n' + FORM_URL,
            'channelName': 'relationship-💕'
        })
        set_last_updated('discord_relationshipCheckIn')



    #### Reading notifications
    book_messages = get_book_progress()
    if book_messages:
        bot_messages.append({
            'messageStr': "**Here are Forrest's reading updates**:\n" + '\n'.join(book_messages),
            'channelName': 'reading-nook-📖'
        })
        set_last_updated('discord_readingUpdates')

    start_bot(forrest_events, angele_events, bot_messages)


if __name__ == '__main__':
    main()
