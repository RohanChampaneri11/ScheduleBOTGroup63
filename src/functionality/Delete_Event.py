# functionality/Delete_event.py

import sys
import discord
import asyncio
from googleapiclient.errors import HttpError
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".../")))

from functionality.highlights import convert_to_12
from functionality.shared_functions import (
    read_event_file,
    create_event_tree,
    delete_event_from_file
)
from functionality.Google import connect_google  # Ensure correct import path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def delete_event(ctx, bot_instance):
    """
    Function:
        delete_event
    Description:
        Deletes an existing event from the user's schedule file and Google Calendar
    Input:
        ctx: the current context
        bot_instance: the instance of the bot
    Output:
        - A reply saying whether the event was deleted or not
    """

    user_id = str(ctx.author.id)
    channel = await ctx.author.create_dm()
    await channel.send("Retrieving your events...")

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    # Open and read user's calendar file
    create_event_tree(user_id)
    rows = read_event_file(user_id)
    logger.debug(f"User ID: {user_id}")

    # Initialize variables
    events = []

    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
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
                    colour=discord.Colour.magenta(),
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

    # Prompt user to select the event to delete
    await channel.send("Please enter the **number** of the event you want to delete:")

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
        event_to_delete = events[selection]
    except asyncio.TimeoutError:
        await channel.send("You took too long to respond. Please try deleting the event again.")
        return
    except Exception:
        await channel.send("Invalid selection. Please try deleting the event again.")
        return

    # Connect to Google Calendar and get service
    service = await connect_google(ctx)
    if service is None:
        await channel.send("Failed to connect to Google Calendar. Cannot proceed with deletion.")
        return

    # Delete the event from Google Calendar
    try:
        service.events().delete(calendarId='primary', eventId=event_to_delete['id']).execute()
        logger.info(f"Event '{event_to_delete['name']}' deleted from Google Calendar.")
        await channel.send(f"The event '{event_to_delete['name']}' has been deleted from your Google Calendar.")
    except HttpError as e:
        if e.resp.status == 404:
            logger.error(f"Event not found in Google Calendar: {e}")
            await channel.send("The event was not found in Google Calendar. It might have already been deleted.")
        else:
            logger.error(f"An error occurred while deleting the event: {e}")
            await channel.send("An error occurred while deleting the event from Google Calendar.")
        return
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        await channel.send("An unexpected error occurred while deleting the event.")
        return

    # Delete the event from local storage
    try:
        delete_event_from_file(user_id, event_to_delete)
        logger.info(f"Event '{event_to_delete['name']}' deleted from local schedule.")
        await channel.send(f"The event '{event_to_delete['name']}' has been deleted from your schedule.")
    except Exception as e:
        logger.error(f"Error deleting event from local file: {e}")
        await channel.send("Failed to delete the event from your schedule file.")
        return
