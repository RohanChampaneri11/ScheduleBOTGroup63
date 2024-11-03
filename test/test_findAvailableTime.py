"""
TESTING Find available time based on the preferred time and events
"""

from datetime import datetime
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))
from src.functionality.FindAvailableTime import findInter, findIntersection
from src.Event import Event

def test_find_one():
    elist = []
    # Create one event
    start = "2021-11-01 11:00:00"
    end = "2021-11-01 12:00:00"
    e1 = Event("Make test cases", start, end, 1, "homework", "Make test cases for my code in SE")
    elist.append(e1)
    date = "11/01/21"
    range1 = datetime.strptime("11/01/21 10:00 am", "%m/%d/%y %I:%M %p")
    range2 = datetime.strptime("11/01/21 06:00 pm", "%m/%d/%y %I:%M %p")
    inte = findIntersection(date, range1, range2, elist)
    assert len(inte) == 2
    msg = inte[0].get('start').strftime("%Y-%m-%d %H:%M:%S") + " - " + inte[0].get('end').strftime("%Y-%m-%d %H:%M:%S")
    assert msg == "2021-11-01 10:00:00 - 2021-11-01 11:00:00"
    msg = inte[1].get('start').strftime("%Y-%m-%d %H:%M:%S") + " - " + inte[1].get('end').strftime("%Y-%m-%d %H:%M:%S")
    assert msg == "2021-11-01 12:00:00 - 2021-11-01 18:00:00"



def test_find():
    elist = []
    # Create two events
    start = "2021-11-01 11:00:00"
    end = "2021-11-01 12:00:00"
    e1 = Event("Make test cases", start, end, 1, "homework", "Make test cases for my code in SE")
    elist.append(e1)
    start = "2021-11-01 13:30:00"
    end = "2021-11-01 14:00:00"
    e2 = Event("Make another test cases", start, end, 1, "homework", "Make another test cases for my code in SE")
    elist.append(e2)
    date = "11/01/21"
    range1 = datetime.strptime("11/01/21 10:00 am", "%m/%d/%y %I:%M %p")
    range2 = datetime.strptime("11/01/21 06:00 pm", "%m/%d/%y %I:%M %p")
    inte = findIntersection(date, range1, range2, elist)
    assert len(inte) == 3
    msg = inte[0].get('start').strftime("%Y-%m-%d %H:%M:%S") + " - " + inte[0].get('end').strftime("%Y-%m-%d %H:%M:%S")
    assert msg == "2021-11-01 10:00:00 - 2021-11-01 11:00:00"
    msg = inte[1].get('start').strftime("%Y-%m-%d %H:%M:%S") + " - " + inte[1].get('end').strftime("%Y-%m-%d %H:%M:%S")
    assert msg == "2021-11-01 12:00:00 - 2021-11-01 13:30:00"
    msg = inte[2].get('start').strftime("%Y-%m-%d %H:%M:%S") + " - " + inte[2].get('end').strftime("%Y-%m-%d %H:%M:%S")
    assert msg == "2021-11-01 14:00:00 - 2021-11-01 18:00:00"



