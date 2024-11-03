import pytest
import os
import sys
from datetime import datetime
from datetime import timedelta
from datetime import time
import discord
import discord.ext.commands as commands
import discord.ext.test as test

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.functionality.FindAvailableTime import getEventsOnDate
from src.functionality.shared_functions import create_event_tree, add_event_to_file
from src.Event import Event

@pytest.fixture
def client(event_loop):
    intents = discord.Intents.default()  # or customize the intents you need
    c = discord.Client(loop=event_loop, intents=intents)
    return c


@pytest.fixture
def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot("!", loop=event_loop, intents=intents)

    marks = request.function.pytestmark
    mark = None
    for mark in marks:
        if mark.name == "cogs":
            break

    if mark is not None:
        for extension in mark.args:
            b.load_extension("tests.internal." + extension)

    test.configure(b)
    return b

@pytest.mark.asyncio
async def test_get_events_on_date(bot, client):
    guild = bot.guilds[0]
    channel = guild.text_channels[0]
    message = await channel.send("!day")

    start = datetime(2021, 9, 30, 0, 0)
    end = datetime(2021, 9, 30, 23, 59)

    current = Event("SE project", start, end, 2, "homework", "Finish it")
    create_event_tree(str(message.author.id))
    add_event_to_file(str(message.author.id), current)

    getEventsOnDate(message, start)
