# tests/test_add_event.py

import sys
import os
import discord
from discord.ext import commands
import discord.ext.test as dpytest  # Aliased for clarity
import pytest

# Adjust the path to import modules from src
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))

from functionality.shared_functions import add_event_to_file
from Event import Event
from parse.match import parse_period, parse_period24
from functionality.AddEvent import add_event

@pytest.fixture
def bot():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.command()
    async def test_add(ctx):
        await add_event(ctx, bot)

    print("Configuring dpytest with the bot instance.")
    dpytest.configure(bot)
    print("dpytest configured successfully.")

    # Temporarily remove extension loading to prevent errors
    # Uncomment and adjust the following lines if you need to load extensions
    # try:
    #     bot.load_extension("cogs.your_extension_name")  # Replace with your actual cog path
    # except Exception as e:
    #     print(f"Failed to load extension: {e}")

    return bot

@pytest.mark.asyncio
async def test_add_event(bot):
    # Simulate sending the "!test_add" message
    await dpytest.message("!test_add")

    # Optionally, wait for the bot to process the message
    await asyncio.sleep(0.25)

    # Verify the bot's response
    dpytest.verify().message().content("Event added successfully!")
