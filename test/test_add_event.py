# tests/test_add_event.py

import sys
import os
import discord
from discord.ext import commands
import discord.ext.test as dpytest  # Aliased for clarity
import pytest

from functionality.shared_functions import add_event_to_file
from Event import Event
from parse.match import parse_period, parse_period24
from functionality.AddEvent import add_event

@pytest.fixture
async def bot(event_loop):
    intents = discord.Intents.default()
    intents.message_content = True  # Ensure the bot can read message content
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Configure dpytest with the bot instance
    await dpytest.configure(bot)
    return bot

@pytest.mark.asyncio
async def test_add_event(bot):
    # Simulate sending the "!test_add" message
    await dpytest.message("!test_add")
    # Add any assertions or checks you need after the message is processed
    await asyncio.sleep(0.25)  # Add a short delay if needed for processing

