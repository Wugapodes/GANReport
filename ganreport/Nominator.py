#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


class Nominator:
    def __init__(self, name):
        self.username = name
        self.entries = []

    def add(self, content, index=0):
        self.entries.insert(index, content)

    def print_noms(self):
        n_noms = 0
        link_list = []
        for entry in self.entries:
            n_noms += 1
            link_list.append(str(entry))
        head = "'''" + self.username + "''' (" + str(n_noms) + ")"
        nomlist = ":" + ", ".join(link_list)
        return "\n".join([head, nomlist])
