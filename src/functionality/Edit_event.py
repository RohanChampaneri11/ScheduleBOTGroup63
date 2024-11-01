# functionality/Edit_event.py

import discord
import asyncio
from datetime import datetime
from functionality.shared_functions import (
    read_event_file,
    create_event_tree,
    write_event_file
)
from functionality.Google import connect_google
from googleapiclient.errors import HttpError
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def edit_event(ctx, bot_instance):
    """
    Function:
        edit_event
    Description:
        Edits an existing event in the user's schedule file and Google Calendar
    Input:
        ctx: the current context
        bot_instance: the instance of the bot
    Output:
        - A reply indicating whether the event was edited successfully
    """
    user_id = str(ctx.author.id)
    channel = await ctx.author.create_dm()
    await channel.send("Retrieving your events...")

    def check(m):
        return m.author == ctx.author and m.channel == channel

    # Open and read user's calendar file
    create_event_tree(user_id)
    rows = read_event_file(user_id)
    logger.debug(f"User ID: {user_id}")

    # Initialize variables
    events = []

    # If there are events in the file
    if len(rows) > 1:
        # For every row in the calendar file (skip header)
        for row in rows[1:]:
            # Ensure row has enough columns
            event = {
                'id': row[0],  # eventId from Google Calendar
                'name': row[1],
                'startDateTime': row[2],
                'endDateTime': row[3],
                'priority': row[4],
                'type': row[5],
                'desc': row[6],
                'location': row[7] if len(row) > 7 else 'None',
            }
            events.append(event)

        # Display all events
        if events:
            await channel.send("Here are your scheduled events:")
            for idx, e in enumerate(events, start=1):
                embed = discord.Embed(
                    colour=discord.Colour.blue(),
                    timestamp=ctx.message.created_at,
                    title=f"Event {idx}: {e['name']}"
                )
                embed.set_footer(text=f"Requested by {ctx.author}")
                embed.add_field(name="Start Time:", value=e['startDateTime'], inline=True)
                embed.add_field(name="End Time:", value=e['endDateTime'], inline=True)
                embed.add_field(name="Priority:", value=e['priority'], inline=False)
                embed.add_field(name="Event Type:", value=e['type'], inline=False)
                embed.add_field(name="Location:", value=e.get('location', 'None'), inline=False)
                embed.add_field(name="Description:", value=e.get('desc', 'None'), inline=False)

                await channel.send(embed=embed)
        else:
            await channel.send("You don't have any events scheduled.")
            return
    else:
        await channel.send("Looks like your schedule is empty. You can add events using the '!schedule' command!")
        return

    # Prompt user to select the event to edit
    await channel.send("Please enter the **number** of the event you want to edit:")

    def selection_check(m):
        return (
            m.content.isdigit() and
            1 <= int(m.content) <= len(events) and
            m.channel == channel and
            m.author == ctx.author
        )

    try:
        selection_msg = await bot_instance.wait_for("message", check=selection_check, timeout=60)
        selection = int(selection_msg.content) - 1
        event_to_edit = events[selection]
    except asyncio.TimeoutError:
        await channel.send("You took too long to respond. Please try editing the event again.")
        return
    except Exception as e:
        logger.error(f"Error during event selection: {e}")
        await channel.send("Invalid selection. Please try editing the event again.")
        return

    # Collect new event details
    await channel.send(
        f"You are editing '{event_to_edit['name']}'. Please provide the new details or type 'skip' to keep the current value."
    )

    # Collect new details
    try:
        # Name
        await channel.send("Enter the new event name or type 'skip' to keep it unchanged:")
        name_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        new_name = name_msg.content.strip() if name_msg.content.strip().lower() != 'skip' else event_to_edit['name']

        # Start Date and Time
        await channel.send("Enter the new start date and time (YYYY-MM-DD HH:MM) or type 'skip':")
        start_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        if start_msg.content.strip().lower() != 'skip':
            new_start = start_msg.content.strip()
            # Validate datetime format
            try:
                new_start_dt = datetime.strptime(new_start, "%Y-%m-%d %H:%M")
            except ValueError:
                await channel.send("Invalid date format. Please use YYYY-MM-DD HH:MM.")
                return
        else:
            new_start = event_to_edit['startDateTime']
            new_start_dt = datetime.strptime(new_start, "%Y-%m-%d %H:%M:%S")

        # End Date and Time
        await channel.send("Enter the new end date and time (YYYY-MM-DD HH:MM) or type 'skip':")
        end_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        if end_msg.content.strip().lower() != 'skip':
            new_end = end_msg.content.strip()
            # Validate datetime format
            try:
                new_end_dt = datetime.strptime(new_end, "%Y-%m-%d %H:%M")
            except ValueError:
                await channel.send("Invalid date format. Please use YYYY-MM-DD HH:MM.")
                return
        else:
            new_end = event_to_edit['endDateTime']
            new_end_dt = datetime.strptime(new_end, "%Y-%m-%d %H:%M:%S")

        # Priority
        await channel.send("Enter the new priority or type 'skip':")
        priority_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        new_priority = priority_msg.content.strip() if priority_msg.content.strip().lower() != 'skip' else event_to_edit['priority']

        # Event Type
        await channel.send("Enter the new event type or type 'skip':")
        type_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        new_type = type_msg.content.strip() if type_msg.content.strip().lower() != 'skip' else event_to_edit['type']

        # Description
        await channel.send("Enter the new description or type 'skip':")
        desc_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        new_desc = desc_msg.content.strip() if desc_msg.content.strip().lower() != 'skip' else event_to_edit['desc']

        # Location
        await channel.send("Enter the new location or type 'skip':")
        loc_msg = await bot_instance.wait_for("message", check=check, timeout=60)
        new_location = loc_msg.content.strip() if loc_msg.content.strip().lower() != 'skip' else event_to_edit['location']

    except asyncio.TimeoutError:
        await channel.send("You took too long to respond. Please try editing the event again.")
        return
    except Exception as e:
        logger.error(f"Error collecting new event details: {e}")
        await channel.send("An error occurred while collecting new event details.")
        return

    # Update the event in Google Calendar
    service = await connect_google(ctx)
    if service is None:
        await channel.send("Failed to connect to Google Calendar. Cannot proceed with editing.")
        return

    try:
        # Fetch the event from Google Calendar
        logger.debug(f"Event to edit ID: {event_to_edit['id']}")
        google_event = service.events().get(calendarId='primary', eventId=event_to_edit['id']).execute()
        logger.debug(f"Fetched google_event: {google_event}")

        # Ensure 'start' and 'end' keys exist
        if 'start' not in google_event:
            google_event['start'] = {}
        if 'end' not in google_event:
            google_event['end'] = {}

        # Update fields
        google_event['summary'] = new_name
        google_event['description'] = new_desc
        google_event['location'] = new_location

        # Handle 'start' and 'end' fields
        new_start_iso = new_start_dt.isoformat()
        new_end_iso = new_end_dt.isoformat()
        if 'dateTime' in google_event.get('start', {}):
            # Event has 'dateTime'
            google_event['start']['dateTime'] = new_start_iso
            google_event['end']['dateTime'] = new_end_iso
            google_event['start']['timeZone'] = 'UTC'
            google_event['end']['timeZone'] = 'UTC'
        elif 'date' in google_event.get('start', {}):
            # Event is an all-day event
            google_event['start']['date'] = new_start_dt.date().isoformat()
            google_event['end']['date'] = new_end_dt.date().isoformat()
        else:
            # Default case - set as dateTime
            google_event['start']['dateTime'] = new_start_iso
            google_event['end']['dateTime'] = new_end_iso
            google_event['start']['timeZone'] = 'UTC'
            google_event['end']['timeZone'] = 'UTC'

        # Update the event in Google Calendar
        updated_event = service.events().update(calendarId='primary', eventId=event_to_edit['id'], body=google_event).execute()
        logger.info(f"Event '{event_to_edit['name']}' updated in Google Calendar.")
        await channel.send(f"The event '{new_name}' has been updated in your Google Calendar.")
    except HttpError as e:
        logger.error(f"An error occurred while updating the event in Google Calendar: {e}")
        await channel.send("An error occurred while updating the event in Google Calendar.")
        return
    except Exception as e:
        logger.error(f"Unexpected error during event update: {e}", exc_info=True)
        await channel.send(f"An unexpected error occurred while updating the event: {e}")
        return

    # Update the event in local storage
    try:
        # Update the event in the events list
        updated_event = {
            'id': event_to_edit['id'],
            'name': new_name,
            'startDateTime': new_start_dt.strftime("%Y-%m-%d %H:%M:%S"),
            'endDateTime': new_end_dt.strftime("%Y-%m-%d %H:%M:%S"),
            'priority': new_priority,
            'type': new_type,
            'desc': new_desc,
            'location': new_location,
        }

        # Replace the event in the events list
        events[selection] = updated_event

        # Reconstruct rows
        updated_rows = [rows[0]]  # Header row
        for e in events:
            updated_rows.append([
                e['id'],
                e['name'],
                e['startDateTime'],
                e['endDateTime'],
                e['priority'],
                e['type'],
                e['desc'],
                e['location'],
            ])

        # Write the updated rows back to the CSV file
        write_event_file(user_id, updated_rows)
        logger.info(f"Event '{new_name}' updated in local schedule.")
        await channel.send(f"The event '{new_name}' has been updated in your schedule.")
    except Exception as e:
        logger.error(f"Error updating event in local file: {e}", exc_info=True)
        await channel.send("Failed to update the event in your schedule file.")
        return
