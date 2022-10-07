import os

import discord
from discord.ext import tasks, commands

# custom package found at:
# https://github.com/forrest-herman/python-packages-common/tree/main/google_calendar_integrations
from google_calendar_integrations.gcal_methods import GoogleCalendarAccount
from google_calendar_integrations import cal_utils

from calendar_methods import get_todays_calendar_events, format_events_to_string

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

    events_to_exclude = ['Forrest Herman Preteckt', 'Personal old',
                         'angele.beaulne@gmail.com', 'McMaster Outlook', 'Recurring Reminders', 'Haddon House']

    today_events = get_todays_calendar_events()
    forrest_events = cal_utils.filter_events_by_calendar(
        today_events, events_to_exclude,
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
    else:
        print("No events for Forrest today")

    if (angele_events):
        print(message2)
        await channel.send(message2)
    else:
        print("No events for Angèle today")

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


# bot.run(TOKEN)
client.run(TOKEN)
