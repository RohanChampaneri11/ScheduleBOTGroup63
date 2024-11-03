# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
# Change current working directory so test case can find the source files
import sys
import pytest
import datetime
import discord
import discord.ext.commands as commands
import discord.ext.test as test
from random import randint
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.functionality.highlights import check_start_or_end, convert_to_12, get_highlight, get_date
from src.functionality.shared_functions import create_event_tree, add_event_to_file
from src.Event import Event


NUM_ITER = 1000

@pytest.fixture
def client(event_loop):
    intents = discord.Intents.default()  # or customize the intents you need
    c = discord.Client(loop=event_loop, intents=intents)
    return c


@pytest.fixture
def bot(request, event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot("!", loop=event_loop, intents=intents)

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
async def test_get_free_time_empty(bot, client):
    guild = bot.guilds[0]
    channel = guild.text_channels[0]
    message = await channel.send("!day today")

    await get_highlight(message, 'today')

@pytest.mark.asyncio
async def test_get_free_time(bot, client):
    guild = bot.guilds[0]
    channel = guild.text_channels[0]
    message = await channel.send("!day today")

    start = datetime.datetime(2021, 9, 30, 0, 0)
    end = datetime.datetime(2021, 9, 30, 23, 59)

    current = Event("SE project", start, end, 2, "homework", "Finish it")
    create_event_tree(str(message.author.id))
    add_event_to_file(str(message.author.id), current)

    await get_highlight(message, 'today')

"""
TESTING DATE CHECKING
"""

# Generate one random datetime object between an uniform range
def random_date(start=2020, end=2025):
    # Determine all posible days between the start and end
    start = datetime.date(start, 1, 1)
    end = datetime.date(end, 12, 31)

    # Give me one of them at random
    choices = end - start
    chosen_day = randint(0, choices.days)

    # Get the random date
    date = start + datetime.timedelta(days=chosen_day)

    # add time
    return str(datetime.datetime(date.year, date.month, date.day)).split()[0]


# Test if event starts and ends on the same day
def test_start_and_end():

    # Iterate test NUM_ITER times
    for i in range(NUM_ITER):
        # pick a random date
        day1 = random_date()
        # ending date is the same
        day2 = day1

        # for testing porpose, assume today is the same day
        today = day1
        assert check_start_or_end([day1, day2], today) == 1


# Test if event starts today but ends later
def test_ends_later():

    # Iterate test NUM_ITER times
    for i in range(NUM_ITER):
        # Pick two random dates
        day1 = ""
        day2 = ""
        while day1 == day2:
            day1 = random_date()
            day2 = random_date()

        # day 1 should be the minimum of the two dates
        # day 2 should be the maximum
        day1, day2 = min(day1, day2), max(day1, day2)

        # For testing, assume today is the first day
        today = day1
        print(str(day1) + " " + str(day2) + " " + str(today))
        assert check_start_or_end([day1, day2], today) == True


# Test if event started on an earlier date but ends today
def test_started_earlier():

    # Iterate test NUM_ITER times
    for i in range(NUM_ITER):
        # pick two random dates
        day1 = ""
        day2 = ""
        while day1 == day2:
            day1 = random_date()
            day2 = random_date()

        # day 1 is the minimum of the two, day 2 is the maximum
        day1, day2 = min(day1, day2), max(day1, day2)

        # for testing, assume day 2 is today
        today = day2

        assert check_start_or_end([day1, day2], today) == True


# Test if no event is scheduled for today
def test_no_event():

    # Iterate test NUM_ITER times
    for i in range(NUM_ITER):
        # pick two random dates
        day1 = ""
        day2 = ""
        while day1 == day2:
            day1 = random_date()
            day2 = random_date()

        day1, day2 = min(day1, day2), max(day1, day2)

        # for testing, assume today to be a random date in the
        # range of year 2018-2019
        today = random_date(2018, 2019)

        assert check_start_or_end([day1, day2], today) == 0


"""
TESTING TIME CONVERSION
"""
# returns a datetime object with a random time
def random_time():
    # get a random hour and minute value
    h = randint(0, 23)
    m = randint(0, 59)

    # return datetime object with a fixed date and variable time
    return datetime.datetime(2020, 12, 6, h, m)


# Function to convert time to 12 hour format
def to_12hour(d):
    ampm = "AM" if d.hour < 12 else "PM"
    hour = d.hour % 12
    if hour == 0:
        hour += 12
    return f"{hour}:{d.minute:02.0f} {ampm}"


# Testing the conversion function in file
def test_time_conversion():
    
    # Iterate test NUM_ITER times
    for i in range(NUM_ITER):
        # get random time
        time = random_time()

        # get time string for testing
        str_time = str(time).split()[1][:5]

        assert convert_to_12(str_time) == to_12hour(time)

"""
TESTING get date function
"""
def test_get_date():
    assert str(datetime.date.today()).split()[0] == get_date('today')
    assert str(datetime.date.today() + datetime.timedelta(days=1)).split()[0] == get_date('tomorrow')
    assert str(datetime.date.today() - datetime.timedelta(days=1)).split()[0] == get_date('yesterday')
    assert str(datetime.date.today() - datetime.timedelta(days=1)).split()[0] == get_date('-1')
    assert str(datetime.date.today() + datetime.timedelta(days=1)).split()[0] == get_date('1')
    assert str(datetime.date.today()).split()[0] == get_date(datetime.date.today().strftime("%m/%d/%y"))


