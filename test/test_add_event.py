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
def client():
    intents = discord.Intents.default()  # or customize the intents you need
    c = discord.Client(intents=intents)
    return c

@pytest.fixture
async def bot(request):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", intents=intents)

    # Define the setup hook to initialize the bot
    async def setup_hook():
        await b.add_cog(TestCog(b))

    b.setup_hook = setup_hook

    @b.command()
    async def test_add(ctx):
        await add_event(ctx, b)

    # Load bot extensions if specified
    marks = request.function.pytestmark
    for mark in marks:
        if mark.name == "cogs":
            for extension in mark.args:
                await b.load_extension("tests.internal." + extension)

    await b.login("fake-token")  # Use a dummy token for testing
    await b.connect()
    test.configure(b)
    return b

# Asynchronous test for add_event command
@pytest.mark.asyncio
async def test_add_event(bot):
    ctx = await test.message("!test_add")
    await asyncio.sleep(0.25)
