import asyncio
import sys, os

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))

import pytest
import pandas as pd
import discord
import discord.ext.commands as commands
import discord.ext.test as test
import threading
from icalendar import Calendar
import time
from schedulebot import importfile
from functionality.import_file import verify_csv, convert_time, import_file, get_ics_data

ICS_STRING = "BEGIN:VCALENDAR\n" \
             "PRODID:-//Google Inc//Google Calendar 70.9054//EN\n" \
             "VERSION:2.0\n" \
             "CALSCALE:GREGORIAN\n" \
             "METHOD:PUBLISH\n" \
             "X-WR-CALNAME:Birthdays\n" \
             "X-WR-TIMEZONE:UTC\n" \
             "X-WR-CALDESC:Displays birthdays\, anniversaries\, and other event dates of people in Google Contacts.\n" \
             "BEGIN:VEVENT\n" \
             "DTSTART;VALUE=DATE:20200508\n" \
             "DTEND;VALUE=DATE:20200509\n" \
             "DTSTAMP:20211102T171105Z\n" \
             "UID:2020_BIRTHDAY_self@google.com\n" \
             "X-GOOGLE-CALENDAR-CONTENT-DISPLAY:chip\n" \
             "X-GOOGLE-CALENDAR-CONTENT-ICON:https://calendar.google.com/googlecalendar/i\n" \
             " mages/cake.gif\n" \
             "CLASS:PUBLIC\n" \
             "CREATED:20211029T145140Z\n" \
             "DESCRIPTION:Happy birthday!\n" \
             "LAST-MODIFIED:20211029T145140Z\n" \
             "SEQUENCE:0\n" \
             "STATUS:CONFIRMED\n" \
             "SUMMARY:Happy birthday!\n" \
             "TRANSP:OPAQUE\n" \
             "END:VEVENT\n" \
             "BEGIN:VEVENT\n" \
             "DTSTART;VALUE=DATE:20210508\n" \
             "DTEND;VALUE=DATE:20210509\n" \
             "DTSTAMP:20211102T171105Z\n" \
             "UID:2021_BIRTHDAY_self@google.com\n" \
             "X-GOOGLE-CALENDAR-CONTENT-DISPLAY:chip\n" \
             "X-GOOGLE-CALENDAR-CONTENT-ICON:https://calendar.google.com/googlecalendar/i\n" \
             " mages/cake.gif\n" \
             "CLASS:PUBLIC\n" \
             "CREATED:20211029T145140Z\n" \
             "DESCRIPTION:Happy birthday!\n" \
             "LAST-MODIFIED:20211029T145140Z\n" \
             "SEQUENCE:0\n" \
             "STATUS:CONFIRMED\n" \
             "SUMMARY:Happy birthday!\n" \
             "TRANSP:OPAQUE\n" \
             "END:VEVENT\n" \
             "BEGIN:VEVENT\n" \
             "DTSTART;VALUE=DATE:20220508\n" \
             "DTEND;VALUE=DATE:20220509\n" \
             "DTSTAMP:20211102T171105Z\n" \
             "UID:2022_BIRTHDAY_self@google.com\n" \
             "X-GOOGLE-CALENDAR-CONTENT-DISPLAY:chip\n" \
             "X-GOOGLE-CALENDAR-CONTENT-ICON:https://calendar.google.com/googlecalendar/i\n" \
             " mages/cake.gif\n" \
             "CLASS:PUBLIC\n" \
             "CREATED:20211029T145140Z\n" \
             "DESCRIPTION:Happy birthday!\n" \
             "LAST-MODIFIED:20211029T145140Z\n" \
             "SEQUENCE:0\n" \
             "STATUS:CONFIRMED\n" \
             "SUMMARY:Happy birthday!\n" \
             "TRANSP:OPAQUE\n" \
             "END:VEVENT\n" \
             "END:VCALENDAR"


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
    async def test_import(ctx):
        thread = threading.Thread(target=importfile, args=(ctx, b), daemon=True)
        thread.start()

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
    await test.message("!test_import")
    await asyncio.sleep(.25)


def test_import_ics():
    gcal = Calendar.from_ical(ICS_STRING)

    data = get_ics_data(gcal)

    assert verify_csv(data)


def test_import_ics_empty():
    gcal = Calendar.from_ical("BEGIN:VCALENDAR\n"
                              "END:VCALENDAR")

    data = get_ics_data(gcal)

    assert verify_csv(data)


def test_time():
    old_time = "1998-05-08 10:30:00"
    new_time = convert_time(old_time)

    assert "05/08/98 10:30 am" == new_time


def test_time_pm():
    old_time = "1998-05-08 18:30:00"
    new_time = convert_time(old_time)

    assert "05/08/98 06:30 pm" == new_time


def test_working_csv():
    data = {'ID': [''],
            'Name': ['test'],
            'Start Date': ["1998-05-08 18:30:00"],
            'End Date': ["1998-05-08 18:45:00"],
            'Priority': '1',
            'Type': '',
            'Notes': ''}

    table = pd.DataFrame(data=data)

    assert verify_csv(table)


def test_typo_csv():
    data = {'ID': [''],
            'Name': ['test'],
            'Stert Date': ["1998-05-08 18:30:00"],
            'End Date': ["1998-05-08 18:45:00"],
            'Priority': '1',
            'Type': '',
            'Notes': ''}

    table = pd.DataFrame(data=data)

    assert not verify_csv(table)


def test_missing_column_csv():
    data = {'ID': [''],
            'Name': ['test'],
            'Stert Date': ["1998-05-08 18:30:00"],
            'Priority': '1',
            'Type': '',
            'Notes': ''}

    table = pd.DataFrame(data=data)

    assert not verify_csv(table)
