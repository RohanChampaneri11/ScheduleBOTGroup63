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
async def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", intents=intents)

    @b.command()
    async def test_add(ctx):
        await add_event(ctx, b)

    # Configure the test runner in the asynchronous setup
    test.configure(b)  # Ensure this is called in the bot setup to avoid errors

    # If there are any extensions to load, load them here
    marks = request.function.pytestmark
    for mark in marks:
        if mark.name == "cogs":
            for extension in mark.args:
                await b.load_extension("tests.internal." + extension)

    return b

# Asynchronous test for add_event command
@pytest.mark.asyncio
async def test_add_event(bot):
    await test.message("!test_add")
    await asyncio.sleep(0.25)
