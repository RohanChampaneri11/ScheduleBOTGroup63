import sys
import os
import asyncio
import discord
import discord.ext.commands as commands
import dpytest
import pytest
from datetime import datetime
from functionality.AddEvent import check_complete, add_event  # type: ignore

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))


@pytest.fixture
async def bot(event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", intents=intents)

    @b.command()
    async def test_add(ctx):
        await add_event(ctx, b)  # Call add_event directly without threading

    await dpytest.configure(b)  # Configure dpytest with the bot
    return b


@pytest.mark.asyncio
async def test_add_event(bot):
    await dpytest.message("!test_add")
    await asyncio.sleep(0.25)


def check_variables1():
    return {
        "start": False,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": False,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": [],
    }

def check_variables2():
    return {
        "start": True,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": False,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": [],
    }

def check_variables3():
    return {
        "start": True,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": True,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": [],
    }

def check_variables4():
    return {
        "start": True,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": True,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": ["Hello"],
    }

def test_check():
    assert not check_complete(**check_variables1())
    assert not check_complete(**check_variables2())
    assert check_complete(**check_variables3())
    assert check_complete(**check_variables4())
