import os
import csv
from pathlib import Path
from Event import Event
from datetime import datetime
from cryptography.fernet import Fernet


def get_event_history(user_id):
    """
    Fetches the event history for the given user ID.
    """
    events = read_event_file(user_id)
    past_events = [event for event in events if datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S") < datetime.now()]
    return format_event_history(past_events)

def format_event_history(events):
    """
    Formats the list of events into a human-readable string.
    Parameters:
        events (list): A list of event data.
    Returns:
        str: Formatted string of the user's past events.
    """
    if not events:
        return "You have no past events."

    history_str = "Your past events:\n"
    for event in events:
        # Assuming each event is a list with elements in the order:
        # [event_id, event_name, start_date, end_date, priority, event_type, notes, location]
        history_str += f"- {event[1]} (from {event[2]} to {event[3]})\n"
    
    return history_str

def add_participant_to_event(user_id, event_id):
    # Load events
    events = read_event_file(user_id)
    # Find the event and add the user to the participants
    for event in events:
        if event[0] == event_id:  # Assuming the first column is the event ID
            event.append(user_id)
            break
    # Save the updated events
    write_event_file(user_id, events)

def get_user_event_history(user_id):
    """
    Retrieves the history of events attended by the user.
    Parameters:
        user_id (str): The Discord ID of the user.
    Returns:
        list: A list of past events.
    """
    events = read_event_file(user_id)
    past_events = []
    
    # Assuming the structure of each event is as follows:
    # [event_id, event_name, start_date, end_date, priority, event_type, notes, location]
    # and the first row of the events file is a header
    for event in events[1:]:
        # Check if the event end date is in the past
        end_date = datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S")
        if end_date < datetime.now():
            past_events.append(event)
    
    return past_events

def get_user_participation_history(user_id):
    # Load events
    events = read_event_file(user_id)
    # Filter events where the user participated
    participated_events = [event for event in events if user_id in event]
    # Return a formatted list of events
    return [f"{event[1]} on {event[2]}" for event in participated_events]  # Adjust indexing based on your CSV structure

def create_type_directory():
    """
    Function: create_type_directory
    Description: Creates ScheduleBot type directory in users Documents folder if it doesn't exist
    Input: None
    Output: Creates Type folder if it doesn't exist
    """

    if not os.path.exists(os.path.expanduser("~/Documents/ScheduleBot/Type")):
        Path(os.path.expanduser("~/Documents/ScheduleBot/Type")).mkdir(parents=True, exist_ok=True)


def create_type_file(user_id):
    """
    Function: create_type_file
    Description: Checks if the event type file exists, and creates it if it doesn't
    Input:
        user_id - String representing the Discord ID of the user
    Output: Creates the event type file if it doesn't exist
    """
    if not os.path.exists(os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv"):
        with open(
            os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv",
            "x",
            newline="",
        ) as new_file:
            csvwriter = csv.writer(new_file, delimiter=",")
            csvwriter.writerow(["Event Type", "Start time", "End time"])
        key = check_key(user_id)
        encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv")


def create_type_tree(user_id):
    """
    Function: create_type_tree
    Description: Checks if the event type directory and file exists, and creates them if they don't
    Input:
        user_id - String representing the Discord ID of the user
    Output: Creates the event type folder and file if they don't exist
    """
    create_type_directory()
    create_type_file(user_id)


def read_type_file(user_id):
    """
    Function: read_type_file
    Description: Reads the event type file
    for those event types
    Input:
        user_id - String representing the Discord ID of the user
    Output:
        rows - List of rows
    """

    key = load_key(user_id)
    decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv")


    # Opens the event type file
    with open(
        os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv", "r"
    ) as type_lines:
        type_lines = csv.reader(type_lines, delimiter=",")
        current_row = []
        rows = []
        for line in type_lines:
            for text in line:
                current_row.append(text)
            rows.append(current_row)
            current_row = []

    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv")
    return rows


def turn_types_to_string(user_id):
    """
    Function: turn_types_to_string
    Description: Reads the event types file and turns all of them into a formatted string
    Input:
        user_id - String representing the Discord ID of the user
    Output:
        output - Formatted string of rows in event types file
    """
    output = ""
    space = [12, 5, 5]
    rows = read_type_file(user_id)
    line_number = 0
    for i in rows:
        if line_number != 0:
            output += f"{i[0]:<{space[0]}} Preferred range of {i[1]:<{space[1]}} - {i[2]:<{space[2]}}\n"
        line_number += 1
    return output


def create_event_directory():
    """
    Function: create_event_directory
    Description: Creates ScheduleBot event directory in users Documents folder if it doesn't exist
    Input: None
    Output: Creates Event folder if it doesn't exist
    """
    if not os.path.exists(os.path.expanduser("~/Documents/ScheduleBot/Event")):
        Path(os.path.expanduser("~/Documents/ScheduleBot/Event")).mkdir(parents=True, exist_ok=True)


def create_event_file(user_id):
    """
    Function: create_event_file
    Description: Checks if the calendar file exists, and creates it if it doesn't
    Input:
        user_id - String representing the Discord ID of the user
    Output: Creates the calendar file if it doesn't exist
    """
    # Checks if the calendar file exists, and creates it if it doesn't
    if not os.path.exists(os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv"):
        with open(
            os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv",
            "x",
            newline="",
        ) as new_file:
            csvwriter = csv.writer(new_file, delimiter=",")
            csvwriter.writerow(["ID", "Name", "Start Date", "End Date", "Priority", "Type", "Notes","Location"])

        key = check_key(user_id)
        encrypt_file(key , os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")






def create_event_tree(user_id):
    """
    Function: create_event_tree
    Description: Checks if the calendar directory and file exists, and creates them if they don't
    Input:
        user_id - String representing the Discord ID of the user
    Output: Creates the calendar folder and file if they don't exist
    """
    create_event_directory()
    create_event_file(user_id)


def read_event_file(user_id):
    """
    Function: read_event_file
    Description: Reads the calendar file and creates a list of rows
    Input:
        user_id - String representing the Discord ID of the user
    Output:
        rows - List of rows
    """

    key = load_key(user_id)
    decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")

    # Opens the current user's csv calendar file
    with open(os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv", "r") as calendar_lines:
        calendar_lines = csv.reader(calendar_lines, delimiter=",")
        rows = []
        # Stores the current row in an array of rows if the row is not a new-line character
        # This check prevents an accidental empty lines from being kept in the updated file
        for row in calendar_lines:
            if len(row) > 0:
                rows.append(row)


    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")
    return rows

def add_event_to_file(user_id, current):
    """
    Function: add_event_to_file
    Description: Adds an event to the calendar file in chronological order
    Input:
        user_id - String representing the Discord ID of the user
        current - Event to be added to calendar
    Output: None
    """
    line_number = 0
    rows = read_event_file(user_id)
    # If the file already has events
    if len(rows) > 1:
        for i in rows:
            # Skips check with empty lines
            if len(i) > 0 and line_number != 0:

                # Temporarily turn each line into an Event object to compare with the object we are trying to add
                temp_event = Event(
                    "",
                    datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S"),
                    datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S"),
                    "",
                    "",
                    "",
                    "",
                )
                # If the current Event occurs before the temp Event, insert the current at that position
                if current < temp_event:
                    rows.insert(line_number, [""] + current.to_list())
                    break

                # If we have reached the end of the array and not inserted, append the current Event to the array
                if line_number == len(rows) - 1:
                    rows.insert(len(rows), [""] + current.to_list())
                    break
            line_number += 1
    else:
        rows.insert(len(rows), [""] + current.to_list())
    # Open current user's calendar file for writing
    with open(
        os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv",
        "w",
        newline="",
    ) as calendar_file:
        # Write to column headers and array of rows back to the calendar file
        csvwriter = csv.writer(calendar_file)
        csvwriter.writerows(rows)

    key = load_key(user_id)
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")

def delete_event_from_file(user_id, to_remove):
    rows = read_event_file(user_id)
    typeRows = read_type_file(user_id)
    print("Rowns: "+rows.__str__())

    for row in rows:
        if to_remove['name'] == row[1]:
            rows.remove(row)

    for type_row in typeRows:
        print("Type Row "+type_row.__str__())
        if to_remove['desc'] == str(type_row[0]):
            typeRows.remove(type_row)

    # Open current user's calendar file for writing
    with open(
            os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv",
            "w",
            newline="",
    ) as calendar_file:
        # Write to column headers and array of rows back to the calendar file
        csvwriter = csv.writer(calendar_file)
        csvwriter.writerows(rows)

    key = load_key(user_id)
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")

    with open(
            os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv",
            "w",
            newline="",
    ) as new_file:
        csvwriter = csv.writer(new_file, delimiter=",")
        csvwriter.writerows(typeRows)

    key = check_key(user_id)
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + user_id + "event_types.csv")


def create_key_directory():
    """
    Function: create_event_directory
    Description: Creates ScheduleBot event directory in users Documents folder if it doesn't exist
    Input: None
    Output: Creates Event folder if it doesn't exist
    """
    if not os.path.exists(os.path.expanduser("~/Documents/ScheduleBot/Key")):
        Path(os.path.expanduser("~/Documents/ScheduleBot/Key")).mkdir(parents=True, exist_ok=True)



def check_key(user_id):
    """
    Function: check_key
    Description: Creates ScheduleBot event key in users Documents folder if it doesn't exist
    Input: user_id String representing the Discord ID of the user
    Output: the key for the given user
    """
    create_key_directory()
    if not os.path.exists(os.path.expanduser("~/Documents") + "/ScheduleBot/Key/" + user_id + ".key"):
        key = write_key(user_id)
    else:
        key = load_key(user_id)

    return key


def write_key(user_id):
    """
    Function: write_key
    Description: Generate the key for the user
    Input:
        user_id - String representing the Discord ID of the user
    Output: the writen key
    """
    #Generates a key and save it into a file
    key = Fernet.generate_key()
    with open(os.path.expanduser("~/Documents") + "/ScheduleBot/Key/" + user_id + ".key", "wb") as key_file:
        key_file.write(key)
    return key


def load_key(user_id):
    """
    Function: load_key
    Description: read the key for the user
    Input:
        userid - String representing the Discord ID of the user
    Output: the loaded key
    """
    with open(os.path.expanduser("~/Documents") + "/ScheduleBot/Key/" + user_id + ".key","rb") as filekey:
        key = filekey.read()

    return key


def encrypt_file(key, filepath):
    """
    Function: encrypt_file
    Description: encrypt the given file with the given key
    Input:
        key - key to encrypt
        filepath - filepath to encrypt
    Output: None
    """
    # using the generated key
    fernet = Fernet(key)
    # opening the original file to encrypt
    with open(filepath, 'rb') as file:
        original = file.read()

    # encrypting the file
    encrypted = fernet.encrypt(original)

    # opening the file in write mode and
    # writing the encrypted data
    with open(filepath, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

def decrypt_file(key, filepath):
    """
    Function: decrypt_file
    Description: decrypt the given file with the given key
    Input:
        key - key to decrypt
        filepath - filepath to decrypt
    Output: None
    """
    # using the key
    fernet = Fernet(key)

    # opening the encrypted file
    with open(filepath, 'rb') as enc_file:
        encrypted = enc_file.read()

    # decrypting the file
    decrypted = fernet.decrypt(encrypted)

    # opening the file in write mode and
    # writing the decrypted data
    with open(filepath, 'wb') as dec_file:
        dec_file.write(decrypted)
