# test/conftest.py
import discord
import pytest

@pytest.fixture
def client(event_loop):
    # Define intents as required by your bot
    intents = discord.Intents.default()
    intents.messages = True  # Enable any other specific intents your tests need
    return discord.Client(intents=intents)
