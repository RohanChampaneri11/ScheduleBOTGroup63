# tests/test_shared_functions.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from functionality.shared_functions import (
    read_event_file,
    add_event_to_file,
    check_start_or_end
)  # Adjust imports based on your project structure
from Event import Event  # Adjust import based on your project structure
import pandas as pd

# ----------------------------
# Test for add_event_to_file
# ----------------------------
def test_add_event_to_file():
    """
    Test adding a new event to the event file and verifying it was added successfully.
    """
    # Create a sample Event object without 'id'
    test_event = Event(
        startDateTime="2021-09-29 09:30:00",
        endDateTime="2021-09-29 11:30:00",
        priority="5",
        type="Meeting",
        desc="Test description",
        location="Office"
    )
    
    # Mock user ID
    user_id = "test_user_id"
    
    # Mock the DataFrame to be empty initially
    with patch('functionality.shared_functions.pd.read_csv') as mock_read_csv, \
         patch('functionality.shared_functions.pd.concat') as mock_pd_concat:
         
        # Setup the mock for read_csv to return an empty DataFrame with specific columns
        mock_read_csv.return_value = pd.DataFrame(columns=[
            'ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes'
        ])
        
        # Setup the mock for pd.concat to simulate appending the new row
        mock_pd_concat.return_value = pd.DataFrame([{
            'ID': '',
            'Name': '',
            'Start Date': '',
            'End Date': '',
            'Priority': '',
            'Type': '',
            'Notes': ''
        }])
        
        # Call the function to add the event
        add_event_to_file(user_id, test_event, 'test_event_id')
        
        # Assertions to ensure pandas functions were called correctly
        mock_read_csv.assert_called_once_with(f'events_{user_id}.csv')
        mock_pd_concat.assert_called_once()

# ----------------------------
# Test for read_event_file
# ----------------------------
def test_read_event_file():
    """
    Test reading events from the event file to verify they are correctly written and read back.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.pd.read_csv') as mock_read_csv:
        # Create a mock DataFrame to be returned by read_csv
        mock_df = pd.DataFrame([{
            'ID': 'test123',
            'Name': 'Test Event',
            'Start Date': '2021-09-29 09:30:00',
            'End Date': '2021-09-29 11:30:00',
            'Priority': '5',
            'Type': 'Meeting',
            'Notes': 'Test description'
        }])
        mock_read_csv.return_value = mock_df
        
        # Call the function to read events
        events = read_event_file(user_id)
        
        # Assertions
        mock_read_csv.assert_called_once_with(f'events_{user_id}.csv')
        assert len(events) == 1, "Expected one event in the event file."
        event = events[0]
        assert event['ID'] == 'test123', "Event ID does not match."
        assert event['Name'] == 'Test Event', "Event Name does not match."
        # Add other assertions as necessary

# ----------------------------
# Test for check_start_or_end
# ----------------------------
def test_check_start_or_end():
    """
    Test the check_start_or_end function with various scenarios.
    """
    # Import the function inside the test to avoid circular imports
    from functionality.shared_functions import check_start_or_end  # Adjust import as necessary
    
    # Test case where today is the start date
    result = check_start_or_end(['2022-10-08', '2024-08-08'], '2022-10-08')
    assert result == 2, f"Expected 2, but got {result}"
    
    # Test case where today is the end date
    result = check_start_or_end(['2022-06-06', '2025-05-12'], '2025-05-12')
    assert result == 3, f"Expected 3, but got {result}"
    
    # Test case where today is neither
    result = check_start_or_end(['2022-06-06', '2025-05-12'], '2023-01-01')
    assert result == False, f"Expected False, but got {result}"

# ----------------------------
# Test for importing ICS data
# ----------------------------
def test_import_ics():
    """
    Test importing ICS data and verifying it is processed correctly.
    """
    from functionality.import_file import get_ics_data  # Adjust import as necessary
    from icalendar import Calendar  # Ensure icalendar is installed
    
    ICS_STRING = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test Calendar//EN
BEGIN:VEVENT
UID:test123
DTSTAMP:20210929T093000Z
DTSTART:20210929T093000Z
DTEND:20210929T113000Z
SUMMARY:Test Event
DESCRIPTION:This is a test event.
LOCATION:Office
END:VEVENT
END:VCALENDAR
"""
    gcal = Calendar.from_ical(ICS_STRING)
    
    # Call the function to process ICS data
    data = get_ics_data(gcal)
    
    # Assertions
    assert not data.empty, "DataFrame should not be empty after importing ICS data."
    assert len(data) == 1, "DataFrame should contain exactly one event."
    event = data.iloc[0]
    assert event['ID'] == 'test123', "Event ID does not match."
    assert event['Name'] == 'Test Event', "Event Name does not match."
    assert event['Start Date'] == '2021-09-29 09:30:00', "Start Date does not match."
    assert event['End Date'] == '2021-09-29 11:30:00', "End Date does not match."
    assert event['Priority'] == '', "Priority should be empty."
    assert event['Type'] == '', "Type should be empty."
    assert event['Notes'] == 'This is a test event.', "Notes do not match."

# ----------------------------
# Additional Shared Function Tests
# ----------------------------
# Add more tests related to shared functions as necessary
