import sys, os
import asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as test
import threading
import time

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))

import pytest
from datetime import datetime

from functionality.create_event_type import create_event_type  # type: ignore


@pytest.fixture
def client(event_loop):
    intents = discord.Intents.default()  # or customize the intents you need
    c = discord.Client(loop=event_loop, intents=intents)
    return c


@pytest.fixture
def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", loop=event_loop, intents=intents)

    @b.command()
    async def test_create(ctx):
        thread = threading.Thread(target=create_event_type, args=(ctx, b, "test_alert"), daemon=True)
        thread.start()
        await asyncio.sleep(.25)

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
async def test_import_file(bot):
    await test.message("!test_create")
    await asyncio.sleep(.25)
