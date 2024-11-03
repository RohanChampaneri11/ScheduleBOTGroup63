import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from tempfile import TemporaryDirectory
import os
import sys

# Adjust the import path to match your project structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.functionality.FindAvailableTime import getEventsOnDate
from src.functionality.shared_functions import create_event_tree, add_event_to_file
from src.Event import Event


def test_create_event_and_add_to_file():
    # Use a temporary directory to avoid creating real files in the filesystem
    with TemporaryDirectory() as temp_dir:
        # Create the expected directory structure within temp_dir
        schedulebot_dir = os.path.join(temp_dir, "ScheduleBot", "Event")
        os.makedirs(schedulebot_dir)

        # Define a mock user object with an `author.id` attribute
        mock_ctx = MagicMock()
        mock_ctx.author.id = "test_user"  # Setting a mock `user_id`

        # Patch `os.path.expanduser` to point to our temp_dir for file paths
        with patch("src.functionality.shared_functions.os.path.expanduser", side_effect=lambda x: temp_dir if x == "~/Documents" else x):
            # Define start and end dates for the event
            start = datetime(2021, 9, 30, 0, 0)
            end = datetime(2021, 9, 30, 23, 59)

            # Create a test event
            event = Event("SE project", start, end, 2, "homework", "Finish it")
            event_id = "event_001"

            # Step 1: Initialize the user's event storage using the mock `author.id`
            create_event_tree(mock_ctx.author.id)

            # Step 2: Add the event to the user's file or data structure
            add_event_to_file(mock_ctx.author.id, event, event_id)

            # Step 3: Retrieve events for the specified date
            events_on_date = getEventsOnDate(mock_ctx, start.strftime("%Y-%m-%d"))

            # Debugging Output: Print the retrieved events to check values
            print("Retrieved events:", events_on_date)

            # Step 4: Assertions to verify the event was added and retrieved correctly
            assert len(events_on_date) > 0, "No events found for the specified date"
            assert events_on_date[0].name == "SE project", "Event name does not match"
            assert events_on_date[0].priority == "2", f"Event priority does not match; got {events_on_date[0].priority}"
            assert events_on_date[0].description == "Finish it", "Event description does not match"
