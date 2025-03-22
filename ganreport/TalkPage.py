#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import re

import pywikibot

from ganreport.utils import wiki2datetime

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


class TalkPage:
    def __init__(self, page, site):
        global live
        self.bad = False
        title = page.titleWithoutNamespace
        text = page.text
        if "{{GA nominee" not in text:
            self.nominee = False
        else:
            self.nominee = True
        self.title = title
        self.text = text
        nom_template = re.search(r"{{GA(?: |_)nominee\|(.*?)}}", text)
        raw_params = nom_template.group(1)
        raw_param_split = raw_params.split("|")
        params = {}
        for param_group in raw_param_split:
            param_pair = [x.strip() for x in param_group.split("=")]
            if len(param_pair) != 2:
                try:
                    ts = wiki2datetime(param_pair[0])
                    params["nom_time"] = ts
                except:
                    self.bad = True
            else:
                params[param_pair[0]] = param_pair[1]
        param_names = params.keys()
        if "nominator" in param_names:
            self.nominator = params["nominator"]
        else:
            self.nominator = None
        if "page" in param_names:
            self.rev_num = int(params["page"])
        else:
            self.rev_num = 1
        if "status" in param_names:
            self.status = params["status"]
        else:
            self.status = ""
        if "subtopic" in param_names:
            self.subtopic = params["subtopic"]
        else:
            self.subtopic = None  # Should be Misc eventually
        if "note" in param_names:
            self.note = params["note"]
        else:
            self.note = None
        # time argument to GA nominee not supported

        if self.status != "":
            self.get_reviewer(site)
        else:
            self.reviewer = None

    def get_reviewer(self, site):
        p_name = "Talk:" + self.title + "/GA" + str(self.rev_num)
        page = pywikibot.Page(site, p_name)
        rev_text = page.text
        r = re.search(r"'''Reviewer:'''.*?User:(.*?)(?:\||])", rev_text)
        self.reviewer = r.group(1)
