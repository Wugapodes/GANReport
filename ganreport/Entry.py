#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import re
from datetime import datetime as dt

from ganreport.utils import reviewRegex, wiki2datetime

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


class Entry:
    def __init__(self, matches, line, subsection):
        """
        Attributes:

        self.text, str
        self.status, bool or None
        self.subsection, userinput
        self.bad, bool
        self.badlink, str or None
        self.title, str or None
        self.timestamp, datetime.datetime instance or None
        self.nominator, str
        self.number, int
        """
        global live
        self.text = line
        self._matches = matches
        self.status = None
        self.subsection = subsection
        self.bad = False
        self.badlink = None
        subsSectName = subsection  # subsection.name

        # Get title
        try:
            title = matches.group(1)
        except:
            self.bad = True
            title = None
        self.title = title

        # Get timestamp
        try:
            t = matches.group(4)
            time = wiki2datetime(t)
        except:
            self.bad = True
            time = None
        self.timestamp = time

        try:
            username = self.getUsername(matches.group(3))
        except Exception:
            self.bad = True
            username = None
        self.nominator = username

        try:
            review_num = matches.group(2)
        except:
            review_num = 1
        self.number = review_num
        self.r_timestamp = dt.utcnow()

    def getUsername(self, text):
        if "[[User" in text:
            name = re.search(r"\[\[User.*?:(.*?)(?:\||\]\])", text).group(1)
            return name
        else:
            raise ValueError("Could not get username.")

    def link(self, image=False, length=True, text=None, num=True, r=False):
        if text is None:
            link = str(self)
        else:
            template = "{{GANentry|1="
            template += text
            template += "|2="
            template += self.number
            if self.status is not None:
                template += "|exists=yes"
            template += "}}"
            link = template
        if length:
            if r:
                days = str((dt.utcnow() - self.r_timestamp).days)
            else:
                days = str((dt.utcnow() - self.timestamp).days)
        if self.status is None or not image:
            img = ""
        elif self.status == "H":
            img = "[[Image:Symbol wait.svg|15px|On Hold]] "
        elif self.status == "R":
            img = "[[Image:Searchtool.svg|15px|Under Review]] "
        elif self.status == "2":
            img = "[[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]] "
        if num:
            string = "# " + img + link
        else:
            string = img + link
        if length:
            string = string + " ('''" + days + "''' days)"
        return string

    def add_review(self, status, line):
        self.status = status
        matches = reviewRegex.search(line)
        try:
            t = matches.group(2)
            time = wiki2datetime(t)
            self.r_timestamp = time
        except:
            self.bad = True
            self.r_timestamp = dt.utcnow()

    def __str__(self):
        template = "{{GANentry|1="
        template += self.title
        template += "|2="
        template += self.number
        if self.status is not None:
            template += "|exists=yes"
        template += "}}"
        return template
