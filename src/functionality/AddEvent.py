import os
import traceback
from functionality.shared_functions import create_event_tree, create_type_tree, add_event_to_file, turn_types_to_string
from Event import Event
from parse.match import parse_period, parse_period24
from functionality.create_event_type import create_event_type
from functionality.distance import get_distance
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import asyncio

async def add_event(ctx, client):
    """
    Function:
        add_event
    Description:
        Walks a user through the event creation process
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A new event added to the user's calendar file
        - A message sent to the context saying an event was successfully created
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = []
    await channel.send("Let's add an event!\nWhat is the name of your event?:")
    event_msg = await client.wait_for("message", check=check)
    event_name = event_msg.content.strip()
    event_array.append(event_name)

    await channel.send(
        "Now give me the start & end dates for your event. "
        "You can use 12-hour or 24-hour formatting.\n\n"
        "Format (Start is first, end is second):\n"
        "12-hour: mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm\n"
        "24-hour: mm/dd/yy hh:mm mm/dd/yy hh:mm"
    )

    event_dates = False
    while not event_dates:
        date_array = []
        try:
            event_msg = await client.wait_for("message", check=check, timeout=60)
            msg_content = event_msg.content.strip()

            # Check for 12-hour format
            if any(x in msg_content.lower() for x in ["am", "pm"]):
                parse_result = parse_period(msg_content)
            else:
                parse_result = parse_period24(msg_content)

            start_date = parse_result[0]
            end_date = parse_result[1]

            if start_date and end_date:
                event_array.append(start_date)
                event_array.append(end_date)
                event_dates = True
            else:
                await channel.send(
                    "Invalid dates. Please ensure you're following the correct format."
                )
        except asyncio.TimeoutError:
            await channel.send("You took too long to respond. Event creation cancelled.")
            return
        except Exception as e:
            await channel.send(f"Error parsing dates: {e}. Please try again.")

    # Priority
    event_priority_set = False
    while not event_priority_set:
        await channel.send(
            "How important is this event? Enter a number between 1-5.\n\n"
            "5 - Highest priority.\n"
            "4 - High priority.\n"
            "3 - Medium priority.\n"
            "2 - Low priority.\n"
            "1 - Lowest priority.\n"
        )
        try:
            event_msg = await client.wait_for("message", check=check, timeout=60)
            priority = int(event_msg.content.strip())
            if 1 <= priority <= 5:
                event_array.append(str(priority))
                event_priority_set = True
            else:
                await channel.send("Please enter a number between 1 and 5.")
        except ValueError:
            await channel.send("Invalid input. Please enter a number between 1 and 5.")
        except asyncio.TimeoutError:
            await channel.send("You took too long to respond. Event creation cancelled.")
            return

    # Event Type
    create_type_tree(str(ctx.author.id))
    event_types = turn_types_to_string(str(ctx.author.id))
    await channel.send(
        "Tell me what type of event this is. Here is a list of event types I currently know:\n"
        + event_types
    )
    try:
        event_msg = await client.wait_for("message", check=check, timeout=60)
        event_type = event_msg.content.strip()
        await create_event_type(ctx, client, event_type)
        event_array.append(event_type)
    except asyncio.TimeoutError:
        await channel.send("You took too long to respond. Event creation cancelled.")
        return

    # Location
    await channel.send("What is the location of the event? (Type 'None' for no location)")
    try:
        event_msg = await client.wait_for("message", check=check, timeout=60)
        location = event_msg.content.strip()
        event_array.append(location)
    except asyncio.TimeoutError:
        await channel.send("You took too long to respond. Event creation cancelled.")
        return

    # Travel Time
    if location.lower() != 'none':
        await channel.send("Do you want to block travel time for this event? (Yes/No)")
        try:
            event_msg = await client.wait_for("message", check=check, timeout=60)
            travel_flag = event_msg.content.strip().lower()
            if travel_flag == 'yes':
                await channel.send(
                    "Enter the mode of transport (DRIVING, WALKING, BICYCLING, TRANSIT):"
                )
                mode_msg = await client.wait_for("message", check=check, timeout=60)
                mode = mode_msg.content.strip().upper()

                await channel.send("Enter source address:")
                src_msg = await client.wait_for("message", check=check, timeout=60)
                source = src_msg.content.strip()

                travel_time, maps_link = get_distance(location, source, mode)
                travel_start = event_array[1] - timedelta(seconds=travel_time)
                travel_event = Event(
                    name="Travel to " + event_array[0],
                    start=travel_start,
                    end=event_array[1],
                    priority="1",
                    event_type="Travel",
                    description="",
                    location=source
                )
                await channel.send("Your travel event was successfully created!")
                await channel.send(f"Here is your Google Maps link for navigation: {maps_link}")
                create_event_tree(str(ctx.author.id))
                # Note: Since this travel event is not created in Google Calendar, consider adding it if needed
                add_event_to_file(str(ctx.author.id), travel_event, "local_travel_event_id")
        except asyncio.TimeoutError:
            await channel.send("You took too long to respond. Skipping travel time.")
        except Exception as e:
            traceback.print_exc()
            await channel.send(f"An error occurred while adding travel time: {e}")

    # Description
    await channel.send("Any additional description you want me to add about the event? If not, enter 'done'")
    event_msg = await client.wait_for("message", check=check)
    description = event_msg.content.strip()
    if description.lower() == "done":
        event_array.append("")
    else:
        event_array.append(description)

    # Adding to Google Calendar
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        token_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "json", "token.json")

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        else:
            await channel.send("You are not logged into Google. Please login using the !ConnectGoogle command")
            return

        service = build('calendar', 'v3', credentials=creds)
        new_event = {
            'summary': event_array[0],
            'location': event_array[5],
            'description': event_array[6],
            'start': {
                'dateTime': event_array[1].strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/New_York'
            },
            'end': {
                'dateTime': event_array[2].strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/New_York'
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 60},
                    {'method': 'popup', 'minutes': 5},
                ]
            }
        }
        event = service.events().insert(calendarId='primary', body=new_event).execute()
        event_id = event.get('id')
        event_link = event.get('htmlLink')
        print('Event created: %s' % event_link)
    except Exception as e:
        traceback.print_exc()
        await channel.send("An error occurred while creating the event in Google Calendar.")
        return

    # Creating Event Object and Saving Locally
    try:
        current_event = Event(
            event_array[0],  # name
            event_array[1],  # start_date
            event_array[2],  # end_date
            event_array[3],  # priority
            event_array[4],  # event_type
            event_array[6],  # description
            event_array[5]   # location
        )
        create_event_tree(str(ctx.author.id))
        add_event_to_file(str(ctx.author.id), current_event, event_id)
        await channel.send("Your event was successfully created!")
        await channel.send(f'Event link: {event_link}')
    except Exception as e:
        print(e)
        traceback.print_exc()
        await channel.send(
            "There was an error in creating your event. Make sure your formatting is correct and try creating the event again."
        )