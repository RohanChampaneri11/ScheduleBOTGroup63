# test/conftest.py
import discord
import pytest

@pytest.fixture
def client(event_loop):
    intents = discord.Intents.default()  # Modify based on your bot's requirements
    intents.messages = True  # Enable specific intents as needed
    return discord.Client(intents=intents, loop=event_loop)
