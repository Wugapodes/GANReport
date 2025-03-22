#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

from datetime import datetime as dt
from datetime import timedelta

from ganreport.Entry import Entry
from ganreport.Nominator import Nominator
from ganreport.Section import Section, SubSection
from ganreport.utils import entRegex, wikiTimeStamp

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


class NomPage:
    # Finds GAN entries and returns time stamp, title, and the following line
    def __init__(self, text):
        global live
        self.raw_text = text
        self.text = text.split("\n")
        self.section = []
        self.stats = {
            "noms": 0,
            "inac": 0,
            "ohld": 0,
            "orev": 0,
            "scnd": 0,
        }

    def parse(self, text=None, organize=True, noms=True):
        if text is None:
            text = self.text
        for line in text:
            if "==" in line:  # If line is a (sub-)section heading...
                line = line.strip()
                if "===" in line:  # If line is a subsection heading...
                    subsec = SubSection(line.strip("=").strip(), c_sec)
                    self.section[-1].subsections.append(subsec)
                else:  # If line is a section heading...
                    sec = Section(line.strip("=").strip())
                    self.section.append(sec)
                    if sec.name == "Miscellaneous":
                        sec.subsections.append(None)
                c_sec = self.section[-1]
                continue
            elif "GANentry" in line:  # If line is a GA nom...
                matches = entRegex.search(line)
                s = c_sec.subsections[-1]
                if s is None:
                    s = c_sec
                    sub_name = None
                else:
                    sub_name = s.name
                entry = Entry(matches, line, sub_name)
                s.entries.append(entry)
            elif "GAReview" in line:  # If a review template...
                try:
                    c_entry = c_sec.subsections[-1].entries[-1]
                except:
                    c_entry = c_sec.entries[-1]
                if "on hold" in line:
                    c_entry.add_review("H", line)
                elif "2nd opinion" in line:
                    c_entry.add_review("2", line)
                else:  # Otherwise it's under review.
                    c_entry.add_review("R", line)
        if organize:
            self.organize_noms()
        if noms:
            try:
                self.nominator_stats()
            except AttributeError:
                # Logging removed 3-19-2025 but should this be silent?
                # When does it even run?
                pass

    def organize_noms(self):
        noms = []
        badnoms = []
        for sec in self.section:
            if sec.name == "Miscellaneous":
                s = [sec]
            else:
                s = sec.subsections
            for subsec in s:
                for entry in subsec.entries:
                    if not entry.bad:
                        noms.append(entry)
                    else:
                        badnoms.append(entry)
        noms.sort(key=lambda x: x.timestamp)
        unrev = [x for x in noms if x.status is None]
        unrev.sort(key=lambda x: x.timestamp)
        self.stats["noms"] = len(noms)
        self.stats["inac"] = len(unrev)
        self.stats["ohld"] = len([x for x in noms if x.status == "H"])
        self.stats["orev"] = len([x for x in noms if x.status == "R"])
        self.stats["scnd"] = len([x for x in noms if x.status == "2"])
        cut = dt.utcnow() - timedelta(30)
        overThirty = [x for x in noms if x.timestamp < cut]
        oldestnoms = [x for x in unrev if x.timestamp < cut]
        oldestnoms.sort(key=lambda x: x.timestamp)
        oldestTen = oldestnoms[:10]
        cut = dt.utcnow() - timedelta(7)
        oldHolds = [x for x in noms if x.r_timestamp < cut and x.status == "H"]
        oldRevs = [x for x in noms if x.r_timestamp < cut and x.status == "R"]
        oldScnd = [x for x in noms if x.r_timestamp < cut and x.status == "2"]
        self.nominations = noms  # All nominations regardless of activity.
        self.unreviewed = unrev  # Nominations not under review.
        self.overThirty = overThirty  # All nominations older than 30 days
        self.oldestTen = oldestTen  # The ten oldest unreviewed nomination
        self.oldUnreviewed = oldestnoms  # Unreviewed nominations over 30 days.
        self.oldOnHold = oldHolds
        self.oldReviews = oldRevs
        self.oldSecondOp = oldScnd
        self.badNoms = badnoms

    def nominator_stats(self):
        """Assumes self.organize_noms() has already been run."""
        nominations = self.nominations
        nominators = {}
        # nom_list = [] # Why is this not used? 3-19-2025
        for entry in nominations:
            nom = entry.nominator
            if nom not in nominators:
                nominators[nom] = Nominator(nom)
            n_obj = nominators[nom]
            n_obj.add(entry)
        self.nominators = nominators

    def write_report(self):
        """I think this just writes the whole report out"""
        report = "{{/top}}\n\n"

        oldestTen = self.print_oldest_ten()

        backlog_report = self.print_backlog_report()

        er_sec = "\n== Exceptions report ==\n"
        oldHolds = self.print_oldHolds()
        oldRevs = self.print_oldReviews()
        oldScnd = self.print_oldSecond()
        oldest = self.print_oldest()
        badnoms = self.print_badnoms()
        multinoms = self.print_noms()

        sum_sec = "\n== Summary ==\n"
        summary = self.print_section_summary()

        # Concatenate report sections
        report = report + oldestTen + backlog_report + er_sec + oldHolds
        report = report + oldRevs + oldScnd + oldest + badnoms + multinoms
        report = report + sum_sec + summary + "<!-- Updated at "
        report = report + wikiTimeStamp() + " by WugBot v" + __version__ + " -->\n"
        return report

    def print_oldest_ten(self):
        oldest = self.oldestTen
        print_list = [
            "== Oldest nominations ==",
            "''List of the oldest ten nominations that have had no activity "
            + "(placed on hold, under review or requesting a 2nd opinion)''",
        ] + [x.link() for x in oldest]
        return "\n".join(print_list)

    def print_backlog_report(self):
        projectPath = "/data/project/ganreportbot/"
        global live
        if live == 1:
            back_fname = "backlog_report.txt"
        else:
            back_fname = "beta_backlog_report.txt"
        ts = wikiTimeStamp()
        noms = self.stats["noms"]
        inac = self.stats["inac"]
        ohld = self.stats["ohld"]
        orev = self.stats["orev"]
        scnd = self.stats["scnd"]
        newline = (
            ts
            + " &ndash; "
            + str(noms)
            + " nominations outstanding; "
            + str(inac)
            + " not reviewed; "
            + "[[Image:Symbol wait.svg|15px|On Hold]] x "
            + str(ohld)
            + "; "
            + "[[Image:Searchtool.svg|15px|Under Review]] x "
            + str(orev)
            + "; [[Image:Symbol neutral vote.svg|15px|2nd Opinion "
            + "Requested]] x "
            + str(scnd)
            + "<br />"
        )
        with open(projectPath + back_fname, "r") as f:
            backlog = [line.strip() for line in f]
        self.oldLine = backlog.pop()
        backlog.insert(0, newline)
        backlog = [
            "\n== Backlog report ==",
            "\n".join(backlog),  # backlog[1]
            ":''Previous daily backlogs can be viewed at the "
            + "[[/Backlog archive|backlog archive]].''",
        ]
        with open(projectPath + back_fname, "w") as f:
            f.write(backlog[1])
        return "\n".join(backlog)

    def print_oldHolds(self):
        print_list = ["\n=== Holds over 7 days old ==="] + [
            x.link(r=True) for x in sorted(self.oldOnHold, key=lambda y: y.r_timestamp)
        ]
        return "\n".join(print_list)

    def print_oldReviews(self):
        print_list = [
            "\n=== Old reviews ===",
            ":''Nominations that have been marked under review for 7 days or "
            + "longer.''",
        ] + [
            x.link(r=True) for x in sorted(self.oldReviews, key=lambda y: y.r_timestamp)
        ]
        return "\n".join(print_list)

    def print_oldSecond(self):
        print_list = [
            "\n=== Old requests for 2nd opinion ===",
            ":''Nominations that have been marked requesting a second opinion"
            + " for 7 days or longer.''",
        ] + [
            x.link(r=True)
            for x in sorted(self.oldSecondOp, key=lambda y: y.r_timestamp)
        ]
        return "\n".join(print_list)

    def print_oldest(self):
        print_list = [
            "\n=== Old nominations ===\n",
            ":''All nominations that were added 30 days ago or longer, "
            + "regardless of other activity.''",
        ] + [
            x.link(image=True)
            for x in sorted(self.overThirty, key=lambda y: y.timestamp)
        ]
        return "\n".join(print_list)

    def print_badnoms(self):
        n_bad = len(self.badNoms)
        if n_bad < 1:
            subhead = "None."
        elif n_bad > 1:
            subhead = (
                ":''There are currently " + str(n_bad) + " malformed nominations.''"
            )
        else:
            subhead = ":''There is currently 1 malformed nomination.''"
        print_list = [
            "\n=== Malformed nominations ===",
            subhead,
        ] + [x.badlink for x in self.badNoms]
        return "\n".join(print_list)

    def print_noms(self, cutoff=3):
        nominators = self.nominators
        nom_list = []
        for v in list(nominators.values()):
            if len(v.entries) >= cutoff:
                nom_list.append(v)
        nom_list.sort(key=lambda nominator: len(nominator.entries), reverse=True)
        nom_list = [x.print_noms() for x in nom_list]
        head = "\n== Nominators with multiple nominations =="
        print_list = [head, "\n".join(nom_list)]
        return "\n".join(print_list)

    def print_section_summary(self):
        sections = self.section
        print_list = []
        for sec in sections:
            print_list.append(sec.summary())
        return "\n".join(print_list)
