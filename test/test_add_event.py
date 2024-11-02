import sys
import os
import asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as test
import threading
import time

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))

import pytest
from datetime import datetime

from functionality.shared_functions import add_event_to_file
from Event import Event
from parse.match import parse_period, parse_period24
from functionality.AddEvent import add_event, check_complete  # Ensure correct import path

# Configure fixtures for client and bot
@pytest.fixture
def client(event_loop):
    c = discord.Client(loop=event_loop)
    test.configure(c)
    return c

@pytest.fixture
def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", loop=event_loop, intents=intents)

    @b.command()
    async def test_add(ctx):
        # Start a separate thread to handle add_event asynchronously
        thread = threading.Thread(target=asyncio.run, args=(add_event(ctx, b),), daemon=True)
        thread.start()

    # Load bot extensions
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

# Asynchronous test for add_event command
@pytest.mark.asyncio
async def test_add_event(bot):
    await test.message("!test_add")
    await asyncio.sleep(0.25)

# Helper functions to create variable sets for test cases
def check_variables1():
    output = {
        "start": False,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": False,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": [],
        "location": "",
    }
    return output

def check_variables2():
    output = {
        "start": True,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": False,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": [],
        "location": "None",
    }
    return output

def check_variables3():
    output = {
        "start": True,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": True,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": [],
        "location": "None",
    }
    return output

def check_variables4():
    output = {
        "start": True,
        "start_date": datetime(2021, 9, 29, 21, 30),
        "end": True,
        "end_date": datetime(2021, 9, 29, 23, 30),
        "array": ["Hello"],
        "location": "None",
    }
    return output

# Test check_complete with different variable sets
def test_check():
    example1 = check_variables1()
    example2 = check_variables2()
    example3 = check_variables3()
    example4 = check_variables4()

    assert not (
        check_complete(
            example1["start"],
            example1["start_date"],
            example1["end"],
            example1["end_date"],
            example1["array"],
            example1["location"],
        )
    )
    assert not (
        check_complete(
            example2["start"],
            example2["start_date"],
            example2["end"],
            example2["end_date"],
            example2["array"],
            example2["location"],
        )
    )
    assert check_complete(
        example3["start"],
        example3["start_date"],
        example3["end"],
        example3["end_date"],
        example3["array"],
        example3["location"],
    )
    assert check_complete(
        example4["start"],
        example4["start_date"],
        example4["end"],
        example4["end_date"],
        example4["array"],
        example4["location"],
    )
