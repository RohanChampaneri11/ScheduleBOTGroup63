# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
# Change current working directory so test case can find the source files

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import datetime
import string
from random import randint, choices
import pytest
from src.event_type import event_type
from src.functionality.delete_event_type import delete_type, print_type

def test_delete_type():
    rows=[['hw1', '10:10 am', '12:10 pm'], ['hw2', '11:10 am', '12:20 pm']]
    msg_content1 = "hw1"
    msg_content2= "hw3"
    assert delete_type(rows, msg_content1)== [[['hw2', '11:10 am', '12:20 pm']], 1, 1]
   
def test_delete_type():
    rows=[['hw1', '10:10 am', '12:10 pm'], ['hw2', '11:10 am', '12:20 pm']]
    msg_content1 = "hw1"
    msg_content2= "hw3"
    assert delete_type(rows, msg_content2)== [[['hw1', '10:10 am', '12:10 pm'], ['hw2', '11:10 am', '12:20 pm']], 0, 2]


def test_print_type():
    rows=[['hw1', '10:10 am', '12:10 pm']]
    assert print_type(rows) == [[['hw1', '10:10 am', '12:10 pm']], '\nEvent Type: hw1 prefered time range from 10:10 am to 12:10 pm']
