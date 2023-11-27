# functionality/event_history.py

from .shared_functions import read_event_file
from datetime import datetime

def format_event_history(events):
    """
    Formats the list of events into a human-readable string.
    """
    if not events:
        return "No past events found."

    history_str = "Your past events:\n"
    for event in events:
        history_str += f"- {event[1]} (from {event[2]} to {event[3]})\n"
    return history_str

def get_event_history(user_id):
    """
    Fetches the event history for the given user ID.
    """
    events = read_event_file(user_id)
    past_events = [event for event in events if datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S") < datetime.now()]
    return format_event_history(past_events)
