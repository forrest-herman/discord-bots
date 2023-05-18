import os
import discord
from discord.ext import tasks, commands

from calendar_event_sync.calendar_methods import format_events_to_string

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

DRY_RUN = False

# global variables
book_update = None
forrest_events = None
angele_events = None

client = discord.Client()


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

    message = "**Here are Forrest's calendar events for today**:\n" + \
        format_events_to_string(forrest_events)
    message2 = "**Here are Angèle's calendar events for today**:\n" + \
        format_events_to_string(angele_events)

    if (forrest_events):
        print(message)
        if not DRY_RUN:
            await channel.send(message)
    else:
        print("No events for Forrest today")

    if (angele_events):
        print(message2)
        if not DRY_RUN:
            await channel.send(message2)
    else:
        print("No events for Angèle today")

    if book_update:
        channel = discord.utils.get(guild.channels, name="reading-nook-📖")
        for message in book_update:
            print(message)
            if not DRY_RUN:
                await channel.send(message)

    await client.close()  # exit()


def start_bot(forrest_events_in=[], angele_events_in=[], book_update_in=None):
    global forrest_events
    global angele_events
    global book_update
    forrest_events = forrest_events_in
    angele_events = angele_events_in
    book_update = book_update_in

    client.run(TOKEN)
