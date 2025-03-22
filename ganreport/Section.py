#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import re

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


class Section:
    sctRegex = re.compile(r"==+ (.*?) (==+)")

    def __init__(self, name):
        global live
        self.name = name
        self.subsections = []
        self.entries = []

    def link(self, image=False, text=None, num=0):
        """I may be wrong, but I'm pretty sure there's no reason for There
        to be a nomination in a super section, so it just defaults to zero.
        I should probably ask someone about that though.
        """
        if text is None:
            link = str(self)
        else:
            sec = self.name
            link = "[[Wikipedia:Good article nominations#" + sec + "|" + text + "]]"
        number = num
        string = link + " " + str(number)
        return string

    def summary(self):
        subsections = self.subsections
        if subsections[0] is None:
            n = len(self.entries)
            text = "'''" + self.link(num="") + "''' (" + str(n) + ")"
        else:
            n = sum([len(x.entries) for x in subsections])
            text = "'''" + self.link(num="") + "''' (" + str(n) + ")"
            for subsec in subsections:
                text = text + "\n" + subsec.summary()
        return text

    def __str__(self):
        s = self.name
        return "[[Wikipedia:Good article nominations#" + s + "|" + s + "]]"


class SubSection(Section):
    def __init__(self, name, section):
        Section.__init__(self, name)
        self.entries = []
        self.section = section

    def link(self, image=False, text=None):
        ####  This still needs modification so it actually creates the format
        ####    seen on the report pages.
        if text is None:
            link = str(self)
        else:
            sec = self.subsection
            link = "[[Wikipedia:Good article nominations#" + sec + "|" + text + "]]"
        return link

    def summary(self):
        entries = self.entries
        nHld = len([x for x in entries if x.status == "H"])
        nRev = len([x for x in entries if x.status == "R"])
        nScn = len([x for x in entries if x.status == "2"])
        HldImg = "[[Image:Symbol wait.svg|15px|On Hold]]"
        RevImg = "[[Image:Searchtool.svg|15px|Under Review]]"
        ScnImg = "[[Image:Symbol neutral vote.svg|15px|2nd Opinion Requested]]"
        out = ":'''" + self.link() + "''' (" + str(len(entries)) + ")"
        if nHld > 0:
            out = out + ": " + HldImg + " x " + str(nHld)
        if nRev > 0:
            sep = "; "
            if nHld == 0:
                sep = ": "
            out = out + sep + RevImg + " x " + str(nRev)
        if nScn > 0:
            sep = "; "
            if (nHld == 0) and (nRev == 0):
                sep = ": "
            out = out + sep + ScnImg + " x " + str(nScn)
        return out

    def __str__(self):
        s = self.name
        return "[[Wikipedia:Good article nominations#" + s + "|" + s + "]]"
