import os
from datetime import datetime
import pytest
from src.functionality.shared_functions import (
    add_event_to_file,
    create_event_tree,
    read_event_file,
    create_event_file,
)
from src.functionality.Event import Event  # Ensure Event is correctly imported

# Test user ID to simulate user-specific event data
test_user_id = "TestUser"

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """
    Fixture to set up the test environment. Creates necessary files and directories,
    and cleans up after all tests.
    """
    # Create the event directory and file
    create_event_tree(test_user_id)
    yield
    # Cleanup: remove test files and directories after tests are completed
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{test_user_id}.csv")
    type_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Type/{test_user_id}event_types.csv")
    if os.path.exists(event_file_path):
        os.remove(event_file_path)
    if os.path.exists(type_file_path):
        os.remove(type_file_path)

def test_create_event_tree():
    """
    Test that the create_event_tree function creates the necessary directory and file for events.
    """
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{test_user_id}.csv")
    # Check if the file was created
    assert os.path.exists(event_file_path), "Event file was not created by create_event_tree."

def test_add_event_to_file():
    """
    Test adding a new event to the event file and verifying it was added successfully.
    """
    # Create a sample Event object
    test_event = Event(
        id="test123",
        startDateTime=datetime(2021, 9, 29, 20, 30).strftime("%Y-%m-%d %H:%M:%S"),
        endDateTime=datetime(2021, 9, 29, 20, 45).strftime("%Y-%m-%d %H:%M:%S"),
        priority="Low",
        type="TestEvent",
        desc="Test description",
        location="Test Location"
    )

    # Add the event to the file
    add_event_to_file(test_user_id, test_event, test_event.id)

    # Read the events to check if the event was added
    events = read_event_file(test_user_id)
    assert any(event[0] == "test123" for event in events), "Event was not found in the file after adding."

def test_read_event_file():
    """
    Test reading events from the event file to verify they are correctly written and read back.
    """
    # Read the events for the test user
    events = read_event_file(test_user_id)

    # Ensure at least one event exists (from test_add_event_to_file)
    assert len(events) > 0, "No events found in the event file after writing."

    # Verify details of the added event
    event = next((e for e in events if e[0] == "test123"), None)
    assert event is not None, "Specific event not found in the file."
    assert event[1] == "test123", "Event ID mismatch."
    assert event[4] == "Low", "Event priority mismatch."

def test_create_event_file():
    """
    Test the create_event_file function to check if the event file is created properly.
    """
    # Remove the file if it already exists to simulate a clean state
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{test_user_id}.csv")
    if os.path.exists(event_file_path):
        os.remove(event_file_path)

    # Run the create_event_file function to create the file
    create_event_file(test_user_id)

    # Check if the file was created
    assert os.path.exists(event_file_path), "Event file was not created by create_event_file."
