#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import datetime
import re

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"

entRegex = re.compile(
    r"{{GANentry.*?\|1=(.*?)\|2=(\d+).*?}}\s*(.*?) (\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)"
)

reviewRegex = re.compile(
    r"{{GAReview.*?}}\s*.*?\[\[User\:(.*?)(?:\||\]\]).*? (\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)"
)


def wiki2datetime(wikistamp):
    time, date_ = wikistamp.split(", ")
    hour, minute = time.split(":")
    day, month, year = date_.split(" ")
    month = monthConvert(month)
    dtVals = [int(year), int(month), int(day), int(hour), int(minute)]
    dt = datetime.datetime(*dtVals)
    return dt


def monthConvert(name):
    """
    Takes in either the name of the month or the number of the month and returns
    the opposite. An input of str(July) would return int(7) while an input of
    int(6) would return str(June).
    Takes:   int OR string
    Returns: string OR int
    """
    if type(name) is str:
        if name == "January":
            return 1
        elif name == "February":
            return 2
        elif name == "March":
            return 3
        elif name == "April":
            return 4
        elif name == "May":
            return 5
        elif name == "June":
            return 6
        elif name == "July":
            return 7
        elif name == "August":
            return 8
        elif name == "September":
            return 9
        elif name == "October":
            return 10
        elif name == "November":
            return 11
        elif name == "December":
            return 12
        else:
            raise ValueError
    elif type(name) is int:
        if name == 1:
            return "January"
        elif name == 2:
            return "February"
        elif name == 3:
            return "March"
        elif name == 4:
            return "April"
        elif name == 5:
            return "May"
        elif name == 6:
            return "June"
        elif name == 7:
            return "July"
        elif name == 8:
            return "August"
        elif name == 9:
            return "September"
        elif name == 10:
            return "October"
        elif name == 11:
            return "November"
        elif name == 12:
            return "December"
        else:
            raise ValueError


def wikiTimeStamp():
    """
    Returns the current time stamp in the style of wikipedia signatures.
    """
    stamp = (
        str(datetime.datetime.utcnow().hour).zfill(2)
        + ":"
        + str(datetime.datetime.utcnow().minute).zfill(2)
        + ", "
        + str(datetime.datetime.utcnow().day)
        + " "
        + monthConvert(datetime.datetime.utcnow().month)
        + " "
        + str(datetime.datetime.utcnow().year)
        + " (UTC)"
    )
    return stamp
