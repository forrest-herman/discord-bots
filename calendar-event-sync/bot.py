import datetime
import os

import discord
from discord.ext import tasks, commands

# custom package found at:
# https://github.com/forrest-herman/python-packages-common/tree/main/google_calendar_integrations
from google_calendar_integrations.gcal_methods import GoogleCalendarAccount
from google_calendar_integrations import cal_utils

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


client = discord.Client()
bot = commands.Bot(command_prefix='/')


@client.event
async def on_ready():
    # alternative
    # guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    channel = discord.utils.get(guild.channels, name="calendar-events")

    today_events = get_todays_calendar_events()
    forrest_events = cal_utils.filter_events_by_calendar(
        today_events, ['Forrest Herman Preteckt', 'Personal old', 'angele.beaulne@gmail.com'],
        exclude=True
    )
    angele_events = cal_utils.filter_events_by_calendar(today_events, ['angele.beaulne@gmail.com'])

    message = "**Here are Forrest's calendar events for today**:\n" + \
        format_events_to_string(forrest_events)
    message2 = "**Here are Angèle's calendar events for today**:\n" + \
        format_events_to_string(angele_events)

    if (forrest_events):
        print(message)
        await channel.send(message)
    if (angele_events):
        print(message2)
        await channel.send(message2)

    exit()

# old
# @bot.command(name='events', help='List all calendar events')
# async def get_calendar_events(ctx):
#     message = "**Here are Forrest's calendar events for today**:\n" + get_todays_calendar_events()
#     await ctx.send(message)


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    exit()

# ----------------
# move to new file
# ----------------

def get_todays_calendar_events():
    # get all calendar events for the current day
    today_start = datetime.datetime.now(datetime.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + datetime.timedelta(days=1)

    # format the times for the API
    today_start = today_start.isoformat()
    today_end = today_end.isoformat()

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
            orderBy='startTime'
        )
    except Exception as e:
        print("Error with GCal API", e)

    events_today_info = [
        {
            'summary': event['summary'],
            'calendar': event['calendar'],
            'start': cal_utils.get_datetime_from_event(event['start']),
            # basically: event['end']['dateTime'] or event['end']['date']
            'end': cal_utils.get_datetime_from_event(event['end'])
        } for event in events_from_all_calendars
    ]

    events_today_info.sort(key=lambda x: x['start'])

    return events_today_info


# utils

def format_events_to_string(events_list):
    events_str_formatted = "\n".join(
        (f"{event['summary']} " + "({} - {})".format(
            event['start'].strftime("%#I:%M %p"),
            event['end'].strftime("%#I:%M %p")
        )) for event in events_list
    )
    return events_str_formatted


# bot.run(TOKEN)
client.run(TOKEN)
