from datetime import datetime
import os
import csv
from datetime import timedelta
from datetime import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".../")))
from src.Event import Event
from src.functionality.export_file import load_key, encrypt_file, decrypt_file


async def get_free_time(ctx, bot):
    """
    Function:
        get_free_time
    Description:
        giving the user the free time today according to the registered events by calling the function compute_free_time
    Input:
        ctx - Discord context window
        bot - Discord bot user
    Output:
        - A message sent to the user channel stating every free time slot that is avaliable today
    """
    channel = await ctx.author.create_dm()

    # check if the user has a completely empty schedule
    if not os.path.exists(os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv"):
        await channel.send('You do not have any event at all')
        return

    rows = []

    # decrypting the file
    key = load_key(str(ctx.author.id))
    decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv")

    # open the calendar file and read the events
    with open(
            os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv", "r"
    ) as calendar_lines:
        calendar_lines = csv.reader(calendar_lines, delimiter=",")

        for row in calendar_lines:
            if len(row) > 0:
                rows.append(row)

    calendarDates = []
    rows.pop(0)
    for i in rows:
        if len(i) > 0:
            datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S"),
            temp_event = Event(
                "",
                datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S"),
                datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S"),
                "",
                "",
                "",
            )
            calendarDates.append(temp_event)
    output = compute_free_time(calendarDates)
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + str(ctx.author.id) + ".csv")
    await channel.send(output)


def compute_free_time(calendarDates):
    """
    Function:
        compute_free_time
    Description:
        returning a string that contains the user the free time according to the registered events
    Input:
        calendarDates - list of the events that the user has in the calendar
    Output:
        - a string stating every free time slot that is avaliable today
    """

    # defining  variable for the output string that the function will returns
    output = ''

    # two constants for the time at the start and end of the day
    start_time = time(hour=0, minute=0)
    end_time = time(hour=23, minute=58)

    # constant = 1 minute in time
    one_min = timedelta(hours=0, minutes=1)

    # setting up variables for the following dates: today , start and end of this current week

    today = datetime.today()

    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(7)

    # adding only the events that are happening today
    today_events = []
    for e in calendarDates:
        if e.start_date.date() == today.date() or e.end_date.date() == today.date():
            today_events.append(e)

    # check if the user has no event for today

    if len(today_events) == 0:
        return 'You do not have any event for today'
    # checks if the user only has one event for today and it starts at 00:00
    elif len(today_events) == 1 and today_events[0].start_date.time() == start_time:
        free_time_start = (today_events[0].end_date + one_min).time()
        return 'Free time from ' + str(free_time_start) + ' until end of the day\n'
    # Cases where the event doesn't start at 00:00
    elif len(today_events) == 1:
        return 'Free time from 00:00 until ' + str((today_events[0].start_date - one_min).time()) + ' and from ' + \
               str((today_events[0].end_date + one_min).time()) + ' until end of the day\n'

    # sorting today's events
    today_events.sort()

    # setting up the first possible free time
    #
    free_time_start = (today_events[0].end_date + one_min).time()
    free_time_end = (today_events[1].start_date - one_min).time()

    # removing the first event if it occurs exactly at 00:00 as there is no free time before it
    # and also showing the first free time if there is a time between the end of the first event and the start of the second event
    # if not , it will show the first free time which occurs exactly at 00:00

    if today_events[0].start_date.time() == start_time and free_time_start < free_time_end:
        output += ('Free time from ' +
                   str(free_time_start) +
                   ' until ' +
                   str(free_time_end) + '\n')
        today_events.pop(0)
    else:
        output += ('Free time from 00:00 until ' + str((today_events[0].start_date - one_min).time()) + '\n')

    # showing free time by iterating through the list of events ignoring the last one as it needs a special case

    for i in range(len(today_events) - 1):
        free_time_start = (today_events[i].end_date + one_min).time()
        free_time_end = (today_events[i + 1].start_date - one_min).time()
        # ignoring if the free time is actually one minute or less
        if free_time_start < free_time_end:
            output += ("Free time from " +
                       str(free_time_start) +
                       ' until ' + str(free_time_end) + '\n')

    # showing the last free time slot if the last event in the day doesn't end exactly at:23:59
    if today_events[-1].end_date.time() < end_time:
        output += ('Free time from ' +
                   str((today_events[-1].end_date + one_min).time())
                   + ' until 23:59 ')

    return output






