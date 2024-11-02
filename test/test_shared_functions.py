# test/test_shared_functions.py

import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import pandas as pd

# Add the src directory to PYTHONPATH to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from functionality.shared_functions import (
    read_event_file,
    add_event_to_file_main,
    get_event_history,
    get_user_event_history,
    get_user_participation_history,
    add_event_to_file,
    delete_event_from_file,
    create_type_directory,
    create_type_file,
    create_type_tree,
    read_type_file,
    turn_types_to_string,
    create_event_directory,
    create_event_file,
    create_event_tree,
    write_event_file,
    encrypt_file,
    decrypt_file,
    format_event_history,
    check_passkey,
    load_key,
    create_key_directory,
    check_key,
    write_key
)
from Event import Event  # Ensure the Event class is accessible


# ----------------------------
# Test for add_event_to_file_main
# ----------------------------
def test_add_event_to_file_main():
    """
    Test adding an event to the user's schedule file using add_event_to_file_main.
    """
    user_id = "test_user_id"
    event_data = {
        'id': 'event123',
        'name': 'Test Event',
        'startDateTime': '2023-10-01 10:00:00',
        'endDateTime': '2023-10-01 12:00:00',
        'priority': 'High',
        'type': 'Meeting',
        'desc': 'Discuss project updates',
        'location': 'Conference Room'
    }

    with patch('functionality.shared_functions.load_key') as mock_load_key, \
         patch('functionality.shared_functions.decrypt_file') as mock_decrypt_file, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file, \
         patch('functionality.shared_functions.csv.writer') as mock_csv_writer, \
         patch('functionality.shared_functions.open', new_callable=MagicMock):

        # Mock the key loading
        mock_load_key.return_value = b'encryptionkey123'

        # Call the function
        add_event_to_file_main(user_id, event_data)

        # Assertions
        mock_load_key.assert_called_once_with(user_id)
        mock_decrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))
        mock_encrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))

        # Ensure csv.writer was called correctly
        assert mock_csv_writer.call_count == 1, "csv.writer should be called once."

        # Additional assertions can be added based on implementation


# ----------------------------
# Test for read_event_file
# ----------------------------
def test_read_event_file():
    """
    Test reading events from the event file to verify they are correctly written and read back.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.load_key') as mock_load_key, \
         patch('functionality.shared_functions.decrypt_file') as mock_decrypt_file, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file, \
         patch('functionality.shared_functions.csv.reader') as mock_csv_reader, \
         patch('functionality.shared_functions.open', mock_open=True):

        # Mock the key loading
        mock_load_key.return_value = b'encryptionkey123'

        # Mock CSV reader
        mock_csv_reader.return_value = [
            ['eventId', 'name', 'startDateTime', 'endDateTime', 'priority', 'type', 'desc', 'location'],
            ['event123', 'Test Event', '2023-10-01 10:00:00', '2023-10-01 12:00:00', 'High', 'Meeting', 'Discuss project updates', 'Conference Room']
        ]

        # Call the function
        events = read_event_file(user_id)

        # Assertions
        mock_load_key.assert_called_once_with(user_id)
        mock_decrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))
        mock_encrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))

        # Verify the returned events
        assert len(events) == 2, "There should be two rows (header and one event)."
        assert events[1][0] == 'event123', "Event ID does not match."
        assert events[1][1] == 'Test Event', "Event name does not match."

# ----------------------------
# Test for get_event_history
# ----------------------------
def test_get_event_history():
    """
    Test fetching the event history for a user.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file:
        # Mock events with one past event
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Past Event', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room'],
            ['event124', 'Future Event', '2030-01-01 10:00:00', '2030-01-01 12:00:00', 'Medium', 'Appointment', 'Discuss future plans', 'Office']
        ]

        # Call the function
        history = get_event_history(user_id)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        assert "Past Event" in history, "Past event should be in the history."
        assert "Future Event" not in history, "Future event should not be in the history."


# ----------------------------
# Test for format_event_history
# ----------------------------
def test_format_event_history():
    """
    Test formatting of event history.
    """
    events = [
        ['event123', 'Past Event 1', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room'],
        ['event124', 'Past Event 2', '2019-05-15 09:00:00', '2019-05-15 10:30:00', 'Low', 'Workshop', 'Team building activities', 'Main Hall']
    ]

    expected_output = (
        "Your past events:\n"
        "- Past Event 1 (from 2020-01-01 10:00:00 to 2020-01-01 12:00:00)\n"
        "- Past Event 2 (from 2019-05-15 09:00:00 to 2019-05-15 10:30:00)\n"
    )

    # Call the function
    formatted_history = format_event_history(events)

    # Assertions
    assert formatted_history == expected_output, "Formatted history does not match expected output."


# ----------------------------
# Test for create_type_directory
# ----------------------------
def test_create_type_directory():
    """
    Test the creation of the type directory.
    """
    with patch('functionality.shared_functions.os.path.exists') as mock_exists, \
         patch('functionality.shared_functions.Path.mkdir') as mock_mkdir:
        
        # Mock that the directory does not exist initially
        mock_exists.return_value = False

        # Call the function
        create_type_directory()

        # Assertions
        mock_exists.assert_called_once_with(os.path.expanduser("~/Documents/ScheduleBot/Type"))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# ----------------------------
# Test for create_type_file
# ----------------------------
def test_create_type_file():
    """
    Test the creation of the type file.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.os.path.exists') as mock_exists, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file, \
         patch('functionality.shared_functions.check_key') as mock_check_key, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file:

        # Mock that the file does not exist
        mock_exists.return_value = False
        mock_check_key.return_value = b'encryptionkey123'

        # Call the function
        create_type_file(user_id)

        # Assertions
        mock_exists.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"))
        mock_file.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"), "x", newline="")
        handle = mock_file()
        handle.write.assert_called_once()
        mock_check_key.assert_called_once_with(user_id)
        mock_encrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"))


# ----------------------------
# Additional Helper for Mocking Open
# ----------------------------
from unittest.mock import mock_open

# ----------------------------
# Test for read_type_file
# ----------------------------
def test_read_type_file():
    """
    Test reading the type file for a user.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.load_key') as mock_load_key, \
         patch('functionality.shared_functions.decrypt_file') as mock_decrypt_file, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file, \
         patch('functionality.shared_functions.csv.reader') as mock_csv_reader, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file:
        
        # Mock the key loading
        mock_load_key.return_value = b'encryptionkey123'

        # Mock CSV reader
        mock_csv_reader.return_value = [
            ['Event Type', 'Start time', 'End time'],
            ['Meeting', '09:00', '10:00'],
            ['Workshop', '11:00', '12:30']
        ]

        # Call the function
        rows = read_type_file(user_id)

        # Assertions
        mock_load_key.assert_called_once_with(user_id)
        mock_decrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"))
        mock_encrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"))
        assert rows == [
            ['Event Type', 'Start time', 'End time'],
            ['Meeting', '09:00', '10:00'],
            ['Workshop', '11:00', '12:30']
        ], "read_type_file did not return the expected rows."


# ----------------------------
# Test for turn_types_to_string
# ----------------------------
def test_turn_types_to_string():
    """
    Test converting event types to a formatted string.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.read_type_file') as mock_read_type_file:
        # Mocked type file rows
        mock_read_type_file.return_value = [
            ['Event Type', 'Start time', 'End time'],
            ['Meeting', '09:00', '10:00'],
            ['Workshop', '11:00', '12:30']
        ]

        # Call the function
        output = turn_types_to_string(user_id)

        # Expected output
        expected_output = (
            "Meeting      Preferred range of 09:00 - 10:00\n"
            "Workshop     Preferred range of 11:00 - 12:30\n"
        )

        # Assertions
        mock_read_type_file.assert_called_once_with(user_id)
        assert output == expected_output, "Formatted string does not match expected output."


# ----------------------------
# Test for create_event_directory
# ----------------------------
def test_create_event_directory():
    """
    Test the creation of the event directory.
    """
    with patch('functionality.shared_functions.os.path.exists') as mock_exists, \
         patch('functionality.shared_functions.Path.mkdir') as mock_mkdir:
        
        # Mock that the directory does not exist initially
        mock_exists.return_value = False

        # Call the function
        create_event_directory()

        # Assertions
        mock_exists.assert_called_once_with(os.path.expanduser("~/Documents/ScheduleBot/Event"))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# ----------------------------
# Test for create_event_file
# ----------------------------
def test_create_event_file():
    """
    Test the creation of the event file.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.os.path.exists') as mock_exists, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file, \
         patch('functionality.shared_functions.check_key') as mock_check_key, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file:

        # Mock that the file does not exist
        mock_exists.return_value = False
        mock_check_key.return_value = b'encryptionkey123'

        # Call the function
        create_event_file(user_id)

        # Assertions
        mock_exists.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))
        mock_file.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"), "x", newline="")
        handle = mock_file()
        handle.write.assert_called_once()
        mock_check_key.assert_called_once_with(user_id)
        mock_encrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))


# ----------------------------
# Test for add_event_to_file
# ----------------------------
def test_add_event_to_file():
    """
    Test adding an event to the file in chronological order.
    """
    user_id = "test_user_id"
    current_event = Event(
        startDateTime="2023-10-01 09:00:00",
        endDateTime="2023-10-01 10:00:00",
        priority="High",
        type="Meeting",
        desc="Team meeting",
        location="Conference Room"
    )
    event_id = "event456"

    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file, \
         patch('functionality.shared_functions.write_event_file') as mock_write_event_file:
        
        # Mock existing events
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Previous Event', '2023-09-30 09:00:00', '2023-09-30 10:00:00', 'Medium', 'Appointment', 'Client meeting', 'Office']
        ]

        # Call the function
        add_event_to_file(user_id, current_event, event_id)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        mock_write_event_file.assert_called_once()

        # Verify that the new event is added in the correct position
        expected_rows = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Previous Event', '2023-09-30 09:00:00', '2023-09-30 10:00:00', 'Medium', 'Appointment', 'Client meeting', 'Office'],
            ['event456', 'Meeting', '2023-10-01 09:00:00', '2023-10-01 10:00:00', 'High', 'Meeting', 'Team meeting', 'Conference Room']
        ]

        mock_write_event_file.assert_called_with(user_id, expected_rows)


# ----------------------------
# Test for delete_event_from_file
# ----------------------------
def test_delete_event_from_file():
    """
    Test deleting an event from the file.
    """
    user_id = "test_user_id"
    to_remove = {'name': 'Test Event', 'desc': 'Discuss project updates'}

    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file, \
         patch('functionality.shared_functions.read_type_file') as mock_read_type_file, \
         patch('functionality.shared_functions.write_event_file') as mock_write_event_file, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file, \
         patch('functionality.shared_functions.check_key') as mock_check_key:

        # Mock existing events and type rows
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Test Event', '2023-10-01 10:00:00', '2023-10-01 12:00:00', 'High', 'Meeting', 'Discuss project updates', 'Conference Room'],
            ['event124', 'Another Event', '2023-10-02 09:00:00', '2023-10-02 11:00:00', 'Low', 'Workshop', 'Training session', 'Main Hall']
        ]
        mock_read_type_file.return_value = [
            ['Event Type', 'Start time', 'End time'],
            ['Meeting', '09:00', '10:00']
        ]

        # Call the function
        delete_event_from_file(user_id, to_remove)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        mock_read_type_file.assert_called_once_with(user_id)
        mock_write_event_file.assert_called_once_with(user_id, [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event124', 'Another Event', '2023-10-02 09:00:00', '2023-10-02 11:00:00', 'Low', 'Workshop', 'Training session', 'Main Hall']
        ])
        mock_encrypt_file.assert_any_call(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))
        mock_encrypt_file.assert_any_call(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"))
        mock_check_key.assert_called_once_with(user_id)


# ----------------------------
# Test for check_passkey
# ----------------------------
def test_check_passkey():
    """
    Test the check_passkey function.
    """
    CLEAR_DATA_PASSKEY = "securepass123"
    
    # Case 1: Correct passkey
    result = check_passkey("securepass123", CLEAR_DATA_PASSKEY)
    assert result == True, "Passkey should be valid."

    # Case 2: Incorrect passkey
    result = check_passkey("wrongpass", CLEAR_DATA_PASSKEY)
    assert result == False, "Passkey should be invalid."


# ----------------------------
# Test for create_key_directory
# ----------------------------
def test_create_key_directory():
    """
    Test the creation of the key directory.
    """
    with patch('functionality.shared_functions.os.path.exists') as mock_exists, \
         patch('functionality.shared_functions.Path.mkdir') as mock_mkdir:
        
        # Mock that the directory does not exist initially
        mock_exists.return_value = False

        # Call the function
        create_key_directory()

        # Assertions
        mock_exists.assert_called_once_with(os.path.expanduser("~/Documents/ScheduleBot/Key"))
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# ----------------------------
# Test for check_key
# ----------------------------
def test_check_key():
    """
    Test the check_key function.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.create_key_directory') as mock_create_key_directory, \
         patch('functionality.shared_functions.os.path.exists') as mock_exists, \
         patch('functionality.shared_functions.load_key') as mock_load_key, \
         patch('functionality.shared_functions.write_key') as mock_write_key:
        
        # Case 1: Key exists
        mock_exists.return_value = True
        mock_load_key.return_value = b'encryptionkey123'

        # Call the function
        key = check_key(user_id)

        # Assertions
        mock_create_key_directory.assert_called_once()
        mock_exists.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key"))
        mock_load_key.assert_called_once_with(user_id)
        mock_write_key.assert_not_called()
        assert key == b'encryptionkey123', "Key should be loaded correctly."

        # Reset mocks for next case
        mock_create_key_directory.reset_mock()
        mock_exists.reset_mock()
        mock_load_key.reset_mock()
        mock_write_key.reset_mock()

        # Case 2: Key does not exist
        mock_exists.return_value = False
        mock_write_key.return_value = b'newencryptionkey456'

        # Call the function
        key = check_key(user_id)

        # Assertions
        mock_create_key_directory.assert_not_called()  # Already called once; depends on function implementation
        mock_exists.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key"))
        mock_load_key.assert_not_called()
        mock_write_key.assert_called_once_with(user_id)
        assert key == b'newencryptionkey456', "New key should be written and returned."


# ----------------------------
# Test for write_key
# ----------------------------
def test_write_key():
    """
    Test the write_key function.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.Fernet.generate_key') as mock_generate_key, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file:
        
        # Mock the key generation
        mock_generate_key.return_value = b'generatedkey123'

        # Call the function
        key = write_key(user_id)

        # Assertions
        mock_generate_key.assert_called_once()
        mock_file.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key"), "wb")
        handle = mock_file()
        handle.write.assert_called_once_with(b'generatedkey123')
        assert key == b'generatedkey123', "Returned key should match the generated key."


# ----------------------------
# Test for load_key
# ----------------------------
def test_load_key():
    """
    Test the load_key function.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.open', mock_open=True) as mock_file:
        # Mock reading the key
        mock_file.return_value.read.return_value = b'encryptionkey123'

        # Call the function
        key = load_key(user_id)

        # Assertions
        mock_file.assert_called_once_with(os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key"), "rb")
        assert key == b'encryptionkey123', "Loaded key should match the expected key."


# ----------------------------
# Test for encrypt_file
# ----------------------------
def test_encrypt_file():
    """
    Test the encrypt_file function.
    """
    key = b'encryptionkey123'
    filepath = "/path/to/file.csv"
    with patch('functionality.shared_functions.Fernet') as mock_fernet_class, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file:
        
        # Mock Fernet instance
        mock_fernet = MagicMock()
        mock_fernet_class.return_value = mock_fernet
        mock_fernet.encrypt.return_value = b'encrypteddata'

        # Call the function
        encrypt_file(key, filepath)

        # Assertions
        mock_fernet_class.assert_called_once_with(key)
        mock_fernet.encrypt.assert_called_once_with(mock_file().read.return_value)
        mock_file.assert_any_call(filepath, 'rb')
        mock_file.assert_any_call(filepath, 'wb')


# ----------------------------
# Test for decrypt_file
# ----------------------------
def test_decrypt_file():
    """
    Test the decrypt_file function.
    """
    key = b'encryptionkey123'
    filepath = "/path/to/file.csv"
    with patch('functionality.shared_functions.Fernet') as mock_fernet_class, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file:
        
        # Mock Fernet instance
        mock_fernet = MagicMock()
        mock_fernet_class.return_value = mock_fernet
        mock_fernet.decrypt.return_value = b'decrypteddata'

        # Call the function
        decrypt_file(key, filepath)

        # Assertions
        mock_fernet_class.assert_called_once_with(key)
        mock_fernet.decrypt.assert_called_once_with(mock_file().read.return_value)
        mock_file.assert_any_call(filepath, 'rb')
        mock_file.assert_any_call(filepath, 'wb')


# ----------------------------
# Test for get_event_history
# ----------------------------
def test_get_event_history():
    """
    Test fetching the event history for a user.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file, \
         patch('functionality.shared_functions.format_event_history') as mock_format_event_history:
        
        # Mock events with one past event
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Past Event', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room']
        ]
        mock_format_event_history.return_value = "Your past events:\n- Past Event (from 2020-01-01 10:00:00 to 2020-01-01 12:00:00)\n"

        # Call the function
        history = get_event_history(user_id)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        mock_format_event_history.assert_called_once_with([
            ['event123', 'Past Event', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room']
        ])
        assert history == "Your past events:\n- Past Event (from 2020-01-01 10:00:00 to 2020-01-01 12:00:00)\n", "Formatted history does not match expected output."


# ----------------------------
# Test for get_user_event_history
# ----------------------------
def test_get_user_event_history():
    """
    Test retrieving the user's event history.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file:
        # Mock events with past and future events
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Past Event 1', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room'],
            ['event124', 'Past Event 2', '2019-05-15 09:00:00', '2019-05-15 10:30:00', 'Low', 'Workshop', 'Team building activities', 'Main Hall'],
            ['event125', 'Future Event', '2030-01-01 09:00:00', '2030-01-01 10:30:00', 'Medium', 'Seminar', 'Learn new skills', 'Auditorium']
        ]

        # Call the function
        past_events = get_user_event_history(user_id)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        assert len(past_events) == 2, "There should be two past events."
        assert past_events == [
            ['event123', 'Past Event 1', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room'],
            ['event124', 'Past Event 2', '2019-05-15 09:00:00', '2019-05-15 10:30:00', 'Low', 'Workshop', 'Team building activities', 'Main Hall']
        ], "Past events do not match expected events."


# ----------------------------
# Test for get_user_participation_history
# ----------------------------
def test_get_user_participation_history():
    """
    Test retrieving the user's participation history.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file:
        # Mock events with user participation
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location', 'Participants'],
            ['event123', 'Event One', '2023-09-01 10:00:00', '2023-09-01 11:00:00', 'High', 'Meeting', 'Project discussion', 'Room 101', 'test_user_id'],
            ['event124', 'Event Two', '2023-10-01 12:00:00', '2023-10-01 13:00:00', 'Medium', 'Workshop', 'Skill development', 'Room 102', 'another_user']
        ]

        # Call the function
        participation_history = get_user_participation_history(user_id)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        assert participation_history == ["Event One on 2023-09-01 10:00:00"], "Participation history does not match expected output."


# ----------------------------
# Test for check_passkey
# ----------------------------
def test_check_passkey():
    """
    Test the check_passkey function.
    """
    CLEAR_DATA_PASSKEY = "securepass123"

    # Case 1: Correct passkey
    result = check_passkey("securepass123", CLEAR_DATA_PASSKEY)
    assert result == True, "Passkey should be valid."

    # Case 2: Incorrect passkey
    result = check_passkey("wrongpass", CLEAR_DATA_PASSKEY)
    assert result == False, "Passkey should be invalid."


# ----------------------------
# Test for write_event_file
# ----------------------------
def test_write_event_file():
    """
    Test writing events back to the event file.
    """
    user_id = "test_user_id"
    rows = [
        ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
        ['event123', 'Test Event', '2023-10-01 10:00:00', '2023-10-01 12:00:00', 'High', 'Meeting', 'Discuss project updates', 'Conference Room']
    ]

    with patch('functionality.shared_functions.load_key') as mock_load_key, \
         patch('functionality.shared_functions.decrypt_file') as mock_decrypt_file, \
         patch('functionality.shared_functions.encrypt_file') as mock_encrypt_file, \
         patch('functionality.shared_functions.open', mock_open=True) as mock_file:
        
        # Mock the key loading
        mock_load_key.return_value = b'encryptionkey123'

        # Call the function
        write_event_file(user_id, rows)

        # Assertions
        mock_load_key.assert_called_once_with(user_id)
        mock_decrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))
        mock_encrypt_file.assert_called_once_with(b'encryptionkey123', os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv"))
        mock_file.assert_called_once_with(os.path.expanduser("~/Documents/ScheduleBot/Event/test_user_id.csv"), "w", newline="")
        handle = mock_file()
        handle.write.assert_called_once()


# ----------------------------
# Additional Helper for Mocking Open
# ----------------------------
from unittest.mock import mock_open

# ----------------------------
# Test for get_user_event_history
# ----------------------------
def test_get_user_event_history():
    """
    Test retrieving the user's event history.
    """
    user_id = "test_user_id"
    with patch('functionality.shared_functions.read_event_file') as mock_read_event_file:
        # Mock events with past and future events
        mock_read_event_file.return_value = [
            ['ID', 'Name', 'Start Date', 'End Date', 'Priority', 'Type', 'Notes', 'Location'],
            ['event123', 'Past Event 1', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room'],
            ['event124', 'Past Event 2', '2019-05-15 09:00:00', '2019-05-15 10:30:00', 'Low', 'Workshop', 'Team building activities', 'Main Hall'],
            ['event125', 'Future Event', '2030-01-01 09:00:00', '2030-01-01 10:30:00', 'Medium', 'Seminar', 'Learn new skills', 'Auditorium']
        ]

        # Call the function
        past_events = get_user_event_history(user_id)

        # Assertions
        mock_read_event_file.assert_called_once_with(user_id)
        assert len(past_events) == 2, "There should be two past events."
        assert past_events == [
            ['event123', 'Past Event 1', '2020-01-01 10:00:00', '2020-01-01 12:00:00', 'High', 'Meeting', 'Discuss past project', 'Conference Room'],
            ['event124', 'Past Event 2', '2019-05-15 09:00:00', '2019-05-15 10:30:00', 'Low', 'Workshop', 'Team building activities', 'Main Hall']
        ], "Past events do not match expected events."


# ----------------------------
# Test for some_other_shared_function
# ----------------------------
def test_some_other_shared_function():
    """
    Example test for another shared function.
    """
    from functionality.shared_functions import some_other_shared_function  # Adjust import as necessary

    # Define inputs and expected outputs
    input_data = "Sample Input"
    expected_output = "Expected Output"

    # Call the function
    actual_output = some_other_shared_function(input_data)

    # Assertion
    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
