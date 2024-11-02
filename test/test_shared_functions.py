import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import os
from functionality.shared_functions import (
    add_event_to_file,
    create_event_tree,
    read_event_file,
    create_event_file,
    check_key,
    load_key,
    write_key,
    encrypt_file,
    decrypt_file,
)
from Event import Event


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


def test_add_event_to_file():
    """
    Test adding a new event to the event file and verifying it was added successfully.
    """
    # Create a sample Event object
    test_event = Event(
        startDateTime="2021-09-29 09:30:00",
        endDateTime="2021-09-29 11:30:00",
        priority="5",
        type="Meeting",
        desc="Test description",
        location="Office"
    )

    # Add the event to the file
    add_event_to_file(test_user_id, test_event, "test123")

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
    assert event[1] == "Test Event", "Event ID mismatch."


def test_key_generation():
    """
    Test that a key is correctly generated, loaded, and encrypted/decrypted.
    """
    with patch("functionality.shared_functions.Fernet") as MockFernet:
        mock_key = b'test_key'
        MockFernet.generate_key.return_value = mock_key

        # Generate a key
        key = write_key(test_user_id)
        assert key == mock_key, "Generated key does not match expected mock key."

        # Load the key and check
        loaded_key = load_key(test_user_id)
        assert loaded_key == key, "Loaded key does not match generated key."


def test_encryption_decryption():
    """
    Test file encryption and decryption.
    """
    test_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{test_user_id}.csv")

    with open(test_file_path, "w") as f:
        f.write("This is a test file.")

    # Encrypt the file
    key = load_key(test_user_id)
    encrypt_file(key, test_file_path)

    # Check that file content is no longer plain text
    with open(test_file_path, "r") as f:
        assert f.read() != "This is a test file.", "File content was not encrypted."

    # Decrypt the file
    decrypt_file(key, test_file_path)

    # Check that file content is restored
    with open(test_file_path, "r") as f:
        assert f.read() == "This is a test file.", "File content was not decrypted correctly."


@pytest.mark.asyncio
async def test_fetch_google_events():
    """
    Test that Google events are fetched correctly.
    """
    mock_ctx = MagicMock()
    mock_service = AsyncMock()
    mock_service.events().list().execute.return_value = {
        'items': [
            {
                'id': 'event123',
                'summary': 'Meeting',
                'start': {'dateTime': '2023-05-01T10:00:00Z'},
                'end': {'dateTime': '2023-05-01T11:00:00Z'},
            }
        ]
    }

    with patch('functionality.shared_functions.connect_google', return_value=mock_service):
        events, error = await fetch_google_events(mock_ctx)

    assert events is not None, "Failed to fetch events."
    assert len(events) == 1, "Unexpected number of events fetched."
    assert events[0]['id'] == 'event123', "Event ID does not match."
