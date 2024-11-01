import re
import datetime
from datetime import date

from functionality.shared_functions import read_event_file, create_event_tree
from functionality.weather import getWeatherData
from functionality.distance import get_lat_log, get_key


async def get_highlight(ctx, arg):
    day = get_date(arg)
    create_event_tree(str(ctx.author.id))
    rows = read_event_file(str(ctx.author.id))

    channel = await ctx.author.create_dm()
    events = []

    for row in rows[1:]:
        event = {
            'name': row[1],
            'startDate': row[2].split()[0],
            'startTime': convert_to_12(row[2].split()[1][:-3]),
            'endDate': row[3].split()[0],
            'endTime': convert_to_12(row[3].split()[1][:-3]),
            'type': row[4],
            'desc': row[5],
            'location': row[7]
        }
        flag = check_start_or_end([event['startDate'], event['endDate']], day)
        event['flag'] = flag

        if flag:
            events.append(event)

    for e in events:
        if e['flag'] == 1:
            await channel.send(f"You have {e['name']} scheduled, from {e['startTime']} to {e['endTime']}")
            
            # Weather report only for events starting and ending today
            if e['name'] != 'Travel' and e['location'] not in ['', 'online', 'Online']:
                latlng = get_lat_log(e['location'], get_key())
                if latlng is not None:
                    humidity, cel, fah, feels_like, desc = getWeatherData(latlng, e['startDate'])
                    weather_message = create_weather_message(fah, feels_like, e['name'], e['startDate'])
                    await channel.send(weather_message)
                else:
                    await channel.send("Could not retrieve location data for weather.")

        elif e['flag'] == 2:
            end_date_formatted = e['endDate'].split('-')
            end_date_formatted = f"{end_date_formatted[1]}/{end_date_formatted[2]}/{end_date_formatted[0]}"
            await channel.send(f"You have {e['name']} scheduled, from {e['startTime']} on {e['startDate']} to {e['endTime']} on {end_date_formatted}")
            
            # Weather report only for events starting today
            if e['name'] != 'Travel' and e['location'] not in ['', 'online', 'Online']:
                latlng = get_lat_log(e['location'], get_key())
                if latlng is not None:
                    humidity, cel, fah, feels_like, desc = getWeatherData(latlng, e['startDate'])
                    weather_message = create_weather_message(fah, feels_like, e['name'], e['startDate'])
                    await channel.send(weather_message)
                else:
                    await channel.send("Could not retrieve location data for weather.")

        elif e['flag'] == 3:
            await channel.send(f"You have {e['name']} scheduled, till {e['endTime']}")

    if not events:
        await channel.send("No events scheduled for " + day + "!")

# Helper functions ...

def create_weather_message(fah, feels_like, event_name, event_date):
    """Function to create weather message based on temperature."""
    if fah < 50:
        return f"It is chilly! 🥶 The temperature is {fah:.1f}°F for {event_name} on {event_date}"
    elif fah < 70:
        return f"Don't forget your Jacket! 🥶 The temperature is {fah:.1f}°F and it feels like {feels_like:.1f}°F for {event_name} on {event_date}"
    else:
        return f"The temperature is {fah:.1f}°F and it feels like {feels_like:.1f}°F for {event_name} on {event_date}"


def get_date(arg):
    if re.match("tomorrow", arg, re.I):
        return str(date.today() + datetime.timedelta(days=1))
    if re.match("yesterday", arg, re.I):
        return str(date.today() - datetime.timedelta(days=1))
    if re.fullmatch(r"\d+", arg):
        return str(date.today() + datetime.timedelta(days=int(arg)))
    if re.fullmatch(r"-\d+", arg):
        return str(date.today() - datetime.timedelta(days=int(arg[1:])))
    if re.fullmatch(r"\d\d/\d\d/\d\d", arg):
        return str(datetime.datetime.strptime(arg, "%m/%d/%y").date())
    if re.match("today", arg, re.I):
        return str(date.today())
    return None


def check_start_or_end(dates, today):
    if today == dates[0] or today == dates[1]:
        return True
    return False


def convert_to_12(time):
    """
    Function:
        convert_to_12
    Description:
        Converts 24-hour time to 12-hour format
    Input:
        - time - time string in 24-hour format
    Output:
        - time string converted to 12-hour format
    """
    if int(time[:2]) > 12:
        new_time = str(int(time[:2]) - 12) + ":" + time[3:] + " PM"
    elif int(time[:2]) == 0:
        new_time = "12:" + time[3:] + " AM"
    elif int(time[:2]) == 12:
        new_time = time + " PM"
    elif int(time[:2]) > 9 and int(time[:2]) < 12:
        new_time = time + " AM"
    else:
        new_time = time[1:] + " AM"
    return new_time
