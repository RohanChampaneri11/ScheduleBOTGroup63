# tests/test_shared_functions.py

import pytest
from datetime import datetime
from functionality.shared_functions import check_start_or_end  # Adjust the import path as necessary

@pytest.mark.asyncio
async def test_add_event_success(mock_ctx, mock_client, mock_google_credentials, mock_google_build):
    """
    Test the add_event function for a successful event creation flow.
    """
    from functionality.AddEvent import add_event  # Import inside to avoid circular dependencies

    # Mock user inputs sequentially
    mock_client.wait_for.side_effect = [
        MagicMock(content="Test Event"),  # Event name
        MagicMock(content="09/29/21 09:30 am 09/29/21 11:30 am"),  # Start and end dates
        MagicMock(content="5"),  # Priority
        MagicMock(content="Meeting"),  # Event type
        MagicMock(content="Office"),  # Location
        MagicMock(content="Yes"),  # Travel time flag
        MagicMock(content="DRIVING"),  # Mode of transport
        MagicMock(content="123 Main St"),  # Source address
        MagicMock(content="This is a test event."),  # Description
    ]

    # Mock external functions and dependencies
    with patch('functionality.AddEvent.create_event_type', AsyncMock()) as mock_create_event_type, \
         patch('functionality.AddEvent.get_distance', return_value=(1800, 'https://maps.google.com/?q=123+Main+St')) as mock_get_distance, \
         patch('functionality.AddEvent.add_event_to_file', MagicMock()) as mock_add_event_to_file, \
         patch('functionality.AddEvent.create_event_tree', MagicMock()) as mock_create_event_tree, \
         patch('functionality.AddEvent.turn_types_to_string', return_value="Meeting, Appointment, Reminder") as mock_turn_types_to_string, \
         patch('functionality.AddEvent.parse_period', return_value=(
             datetime(2021, 9, 29, 9, 30),
             datetime(2021, 9, 29, 11, 30)
         )) as mock_parse_period, \
         patch('functionality.AddEvent.parse_period24', return_value=(None, None)) as mock_parse_period24:
             
            await add_event(mock_ctx, mock_client)

    # Assertions to ensure each step was called correctly
    mock_ctx.author.create_dm.assert_awaited_once()
    assert mock_client.wait_for.call_count == 9, f"Expected 9 wait_for calls, but got {mock_client.wait_for.call_count}"

    # Expected send messages
    expected_messages = [
        "Let's add an event!\nWhat is the name of your event?",
        "Now give me the start & end dates for your event. "
        "You can use 12-hour or 24-hour formatting.\n\n"
        "Format (Start is first, end is second):\n"
        "12-hour: mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm\n"
        "24-hour: mm/dd/yy hh:mm mm/dd/yy hh:mm",
        "How important is this event? Enter a number between 1-5.\n\n"
        "5 - Highest priority.\n"
        "4 - High priority.\n"
        "3 - Medium priority.\n"
        "2 - Low priority.\n"
        "1 - Lowest priority.\n",
        "Tell me what type of event this is. Here is a list of event types I currently know:\nMeeting, Appointment, Reminder",
        "What is the location of the event? (Type 'None' for no location)",
        "Do you want to block travel time for this event? (Yes/No)",
        "Enter the mode of transport (DRIVING, WALKING, BICYCLING, TRANSIT):",
        "Enter source address:",
        "Your travel event was successfully created!",
        "Here is your Google Maps link for navigation: https://maps.google.com/?q=123+Main+St",
        "Any additional description you want me to add about the event? If not, enter 'done'",
        "Your event was successfully created!",
        "Event link: https://calendar.google.com/calendar/event?eid=test_event_id",
    ]

    # Extract actual send calls
    actual_send_calls = [call_args[0][0] for call_args in mock_ctx.send.call_args_list]

    # Compare expected and actual messages
    for expected, actual in zip(expected_messages, actual_send_calls):
        assert expected == actual, f"Expected send message '{expected}', but got '{actual}'"

    # Verify that the event was added to Google Calendar
    mock_google_credentials.assert_called_once()
    mock_google_build.assert_called_once_with('calendar', 'v3', credentials=mock_google_credentials.return_value)
    mock_google_build.return_value.events().insert.assert_called_once()
    mock_google_build.return_value.events().insert.return_value.execute.assert_called_once()

    # Verify that create_event_type was called
    mock_create_event_type.assert_awaited_once_with(mock_ctx, mock_client, "Meeting")

    # Verify that get_distance was called
    mock_get_distance.assert_called_once_with("Office", "123 Main St", "DRIVING")

    # Verify that create_event_tree was called
    mock_create_event_tree.assert_called_once_with(str(mock_ctx.author.id))

    # Verify that turn_types_to_string was called
    mock_turn_types_to_string.assert_called_once_with(str(mock_ctx.author.id))

    # Verify that parse_period was called
    mock_parse_period.assert_called_once_with("09/29/21 09:30 am 09/29/21 11:30 am")
    mock_parse_period24.assert_not_called()

    # Verify that add_event_to_file was called with correct parameters
    expected_event = Event(
        startDateTime="2021-09-29 09:30:00",
        endDateTime="2021-09-29 11:30:00",
        priority="5",
        type="Meeting",
        desc="This is a test event.",
        location="Office"
    )
    mock_add_event_to_file.assert_called_once_with(str(mock_ctx.author.id), expected_event, 'test_event_id')

    # Verify that channel.send was called with the event link
    mock_ctx.send.assert_any_call("Your event was successfully created!")
    mock_ctx.send.assert_any_call('Event link: https://calendar.google.com/calendar/event?eid=test_event_id')
