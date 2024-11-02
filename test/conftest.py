# tests/conftest.py

import pytest
import discord
from discord.ext import commands
from unittest.mock import MagicMock, AsyncMock
from unittest.mock import patch

# Fixture for Discord Intents
@pytest.fixture
def intents():
    return discord.Intents.default()

# Fixture for Discord Client
@pytest.fixture
def client(intents):
    c = discord.Client(intents=intents)
    # Additional configuration if needed
    return c

# Fixture for Discord Bot
@pytest.fixture
def bot(intents):
    b = commands.Bot(command_prefix="!", intents=intents)
    
    @b.command()
    async def test_add(ctx):
        # Import `add_event` inside to avoid circular imports
        from functionality.AddEvent import add_event
        await add_event(ctx, b)
    
    # Load extensions or cogs if necessary
    # Example:
    # b.load_extension('cogs.some_cog')
    
    return b

# Fixture for Mock Context
@pytest.fixture
def mock_ctx():
    """Mock context for Discord commands."""
    ctx = MagicMock()
    ctx.author.id = 123456789
    ctx.author.create_dm = AsyncMock(return_value=MagicMock())
    ctx.send = AsyncMock()
    return ctx

# Fixture for Mock Discord Client
@pytest.fixture
def mock_client():
    """Mock Discord client."""
    client = MagicMock()
    client.wait_for = AsyncMock()
    return client

# Fixture for Mock Google Credentials
@pytest.fixture
def mock_google_credentials():
    """Mock Google Credentials."""
    with patch('google.oauth2.credentials.Credentials') as mock_creds:
        yield mock_creds

# Fixture for Mock Google Calendar API Build
@pytest.fixture
def mock_google_build():
    """Mock Google Calendar API build."""
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().insert().execute = MagicMock(return_value={
            'id': 'test_event_id',
            'htmlLink': 'https://calendar.google.com/calendar/event?eid=test_event_id'
        })
        yield mock_build
