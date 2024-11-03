import sys
import os
import asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as test
import pytest
from datetime import datetime

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))

from functionality.shared_functions import add_event_to_file
from Event import Event
from parse.match import parse_period, parse_period24
from functionality.AddEvent import add_event

# Configure fixtures for client and bot
@pytest.fixture
def client(event_loop):
    intents = discord.Intents.default()  # or customize the intents you need
    c = discord.Client(intents=intents)
    return c

@pytest.fixture
def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", intents=intents)

    @b.command()
    async def test_add(ctx):
        await add_event(ctx, b)

    # Load bot extensions if specified
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

# Asynchronous test for add_event command
@pytest.mark.asyncio
async def test_add_event(bot):
    # Send a message as a simulated command
    ctx = await test.message("!test_add")
    # Wait for the event loop to process
    await asyncio.sleep(0.25)

    # Verify that add_event was called successfully
    # Add assertions here as needed
