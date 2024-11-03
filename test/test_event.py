# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
# Change current working directory so test case can find the source files
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.Event import Event


def create_event_1():
    start = datetime(2021, 9, 29, 20, 21)
    end = datetime(2021, 9, 29, 22, 21)
    return Event("Make test cases", start, end, 1, "homework", "Make test cases for my code in SE")


def create_event_2():
    start = datetime(2021, 9, 30, 0, 0)
    end = datetime(2021, 9, 30, 23, 59)
    return Event("SE project", start, end, 2, "homework", "Finish it")


def create_event_3():
    start = datetime(2021, 9, 30, 14, 0)
    end = datetime(2021, 9, 30, 15, 0)
    return Event( "Coffee time", start, end, 3, "recess", "Enjoy")


def create_event_4():
    start = datetime(2021, 9, 29, 23, 0)
    end = datetime(2021, 9, 30, 10, 0)
    return Event( "Sleep", start, end, 4, "recess", "zzz")


def create_event_5():
    start = datetime(2021, 9, 30, 23, 0)
    end = datetime(2021, 10, 1, 10, 0)
    return Event( "Sleep 2", start, end, 5, "recess", "zzz")


def test_str_1():
    assert str(create_event_1()) == "Make test cases 2021-09-29 20:21:00 2021-09-29 22:21:00 1 homework Make test cases for my code in SE None"


def test_str_2():
    assert str(create_event_2()) == "SE project 2021-09-30 00:00:00 2021-09-30 23:59:00 2 homework Finish it None"


def test_less_than():
    e1 = create_event_1()
    e2 = create_event_2()
    assert e1 < e2
    assert not(e2 < e1)
    assert not(e1 < e1)


def test_less_equal():
    e1 = create_event_1()
    e2 = create_event_2()
    assert e1 <= e2
    assert not(e2 <= e1)
    assert e1 <= e1


def test_greater_than():
    e1 = create_event_1()
    e2 = create_event_2()
    assert not(e1 > e2)
    assert e2 > e1
    assert not(e1 > e1)


def test_greater_equal():
    e1 = create_event_1()
    e2 = create_event_2()
    assert not(e1 >= e2)
    assert e2 >= e1
    assert e1 >= e1


def test_intersect():
    e1 = create_event_1()
    e2 = create_event_2()
    e3 = create_event_3()
    e4 = create_event_4()
    e5 = create_event_5()
    assert not(e1.intersect(e2))
    assert e1.intersect(e1)
    assert e2.intersect(e3)
    assert e2.intersect(e4)
    assert e2.intersect(e5)
    assert e3.intersect(e2)
    assert e4.intersect(e2)
    assert e5.intersect(e2)


def test_to_list():
    e1 = create_event_1()
    list_1 = [e1.name, e1.start_date, e1.end_date, e1.priority, e1.event_type, e1.description]
    for i1, i2 in zip (e1.to_list(), list_1):
        assert i1 == str(i2)
