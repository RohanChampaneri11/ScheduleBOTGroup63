# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
# Change current working directory so test case can find the source files
import sys, os
import datetime
import string
import pytest
from random import randint, choices

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.parse.match import parse_period

NUM_ITER = 1000

# Generate one random datetime object between an uniform range
def random_datetime(start = 2020, end = 2025):
    # Determine all posible days between the start and end
    start = datetime.date(start, 1, 1)
    end = datetime.date(end, 12, 31)

    # Give me one of them at random
    choices = end - start
    chosen_day = randint( 0, choices.days )

    # Randomly pick a time
    h = randint(0, 23)
    m = randint(0, 59)

    # Get the random date
    date = start + datetime.timedelta(days = chosen_day)

    # add time
    return datetime.datetime(date.year, date.month, date.day, h, m)

def to_military(d):
    return f"{d.month:02.0f}/{d.day:02.0f}/{d.year:4.0f} {d.hour}:{d.minute:02.0f}"

def to_12hour(d):
    ampm = "am" if d.hour < 12 else "pm"
    hour = d.hour % 12
    if hour == 0: hour += 12
    return f"{d.month:02.0f}/{d.day:02.0f}/{d.year:4.0f} {hour}:{d.minute:02.0f} {ampm}"

def period_to_string(date1, date2):
    # Convert dates to string input
    s = ""
    for d in [date1, date2]:
        # 50% chance of military or 12 hour
        if randint(0, 1) == 0:
            s += to_military(d)
        else:
            s += to_12hour(d)
        s += " "
    return s

# Test correct date times
def test_correct():
    # Do this test 1000 times
    for i in range(NUM_ITER):
        # Pick 2 random dates
        date1 = random_datetime()
        date2 = random_datetime()
        date1, date2 = min(date1, date2), max(date1, date2)

        s = period_to_string(date1, date2)
        
        # Parse input
        # No try, we know input should be correct
        res_date1, res_date2 = parse_period(s)

        assert res_date1 == date1
        assert res_date2 == date2

# Test inverted date times
# i.e. start date is AFTER ending
def test_swapped():
    # Do this test 1000 times
    for i in range(NUM_ITER):
        # Pick 2 random dates
        date1 = random_datetime()
        date2 = random_datetime()
        date1, date2 = max(date1, date2), min(date1, date2)

        s = period_to_string(date1, date2)

        # It should fail, throw if it does pass
        try:
            res_date1, res_date2 = parse_period(s)
            assert False
        except Exception as e:
            assert str(e) == "your starting date is after your ending date"

# Tests if user inputs an impossible date
# 29 feb in a non-leap year
# 30 feb
# 31 of shorter months
def test_impossible():
    cases = [(2, 29, 2023), (2, 30, 2024)]
    cases += [(x, 31, 2022) for x in [2, 4, 6, 9, 11]]

    # Test as ending dates
    for mm, dd, yyyy in cases:
        date1 = random_datetime(2020, 2021)
        
        s = to_military(date1)
        s += " "
        s += f"{mm:02.0f}/{dd:02.0f}/{yyyy:4.0f} 0:00"

        # It should fail, throw if it does pass
        try:
            res_date1, res_date2 = parse_period(s)
            assert False
        except Exception as e:
            assert str(e) == "your entered date is not possible"
    
    # Test as starting dates
    for mm, dd, yyyy in cases:
        date2 = random_datetime(2025, 2026)
        
        s = f"{mm:02.0f}/{dd:02.0f}/{yyyy:4.0f} 0:00"
        s += " "
        s += to_military(date2)

        # It should fail, throw if it does pass
        try:
            res_date1, res_date2 = parse_period(s)
            assert False
        except Exception as e:
            assert str(e) == "your entered date is not possible"

# Generate random noise
# Random text generation from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
def gibberish():
    text = ''.join(choices(string.ascii_uppercase + string.ascii_letters + " /:"
        , k=randint(0, 62)))
    return text

# Just test random input
def test_gibberish():
    for i in range(NUM_ITER):
        s = gibberish()

        # It should fail, throw if it does pass
        try:
            res_date1, res_date2 = parse_period(s)
            assert False
        except Exception as e:
            # Many reasons why parser could fail, just accept any failure
            assert True
