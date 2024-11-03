import sys
import os
import asyncio
import discord
from discord.ext import commands
import discord.ext.test as dpytest
import pytest
from datetime import datetime

# Adjust the path to import modules from src
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))

from functionality.shared_functions import add_event_to_file
from Event import Event
from parse.match import parse_period, parse_period24
from functionality.AddEvent import add_event

# Synchronous fixture to set up the bot and configure dpytest
@pytest.fixture
def bot():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Define the test_add command
    @bot.command()
    async def test_add(ctx):
        await add_event(ctx, bot)

    # Configure the test runner with the bot instance
    dpytest.configure(bot)

    # Load any extensions if necessary
    # Example of loading an extension synchronously
    try:
        asyncio.run(bot.load_extension("tests.internal.your_extension"))
    except Exception as e:
        print(f"Failed to load extension: {e}")

    return bot

# Asynchronous test for the add_event command
@pytest.mark.asyncio
async def test_add_event(bot):
    # Simulate sending the "!test_add" message
    await dpytest.message("!test_add")

    # Optionally, wait for the bot to process the message
    await asyncio.sleep(0.25)

    # Verify the bot's response
    # Replace "Event added successfully!" with your actual expected response
    dpytest.verify().message().content("Event added successfully!")
