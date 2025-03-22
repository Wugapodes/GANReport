#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import pywikibot
import re
from datetime import date
from datetime import timedelta
from datetime import datetime as dt
import datetime
import sys

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"

########
# Changing this to 1 makes your changes live on the report page, do not set to
# live mode unless you have been approved for bot usage. Do not merge commits
# where this is not default to 0
########
live = 0

entRegex = re.compile(
    r"{{GANentry.*?\|1=(.*?)\|2=(\d+).*?}}\s*(.*?) (\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)"
)
reviewRegex = re.compile(
    r"{{GAReview.*?}}\s*.*?\[\[User\:(.*?)(?:\||\]\]).*? (\d\d\:\d\d, \d+ .*? \d\d\d\d) \(UTC\)"
)


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
            "''List of the oldest ten nominations that have had no activity " \
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


def checkArgs(arg):
    pass


def save_pages(site, report, oldLine, oldTen):
    global live
    try:
        page = pywikibot.Page(site, "Wikipedia:Good article nominations/Report")
    except:
        # Logging removed 3-19-2025 but this should almost certainly not be silent...
        #  but then why did it handle the exception?
        pass
    # Determine if the bot should write to a live page or the test page. Defaults to
    #     test page. Value of -1 tests backlog update (not standard because the file
    #     size is very big).
    if live == 0:
        pass
    elif live == 1:
        page.text = report
        try:
            page.save("Updating exceptions report, WugBot v" + __version__)
        except:
            # Logging removed 3-19-2025 but this should almost certainly not be silent...
            #  but then why did it handle the exception?
            pass
        try:
            page = pywikibot.Page(
                site, "Wikipedia:Good article nominations/" + "Report/Backlog archive"
            )
        except:
            # Logging removed 3-19-2025 but this should almost certainly not be silent...
            #  but then why did it handle the exception?
            pass
        page.text += "\n" + oldLine
        page.save("Update of GAN report backlog, WugBot v" + __version__)
    else:
        page = pywikibot.Page(site, "User:Wugapodes/GANReportBotTest")
        page.text = report
        page.save("Testing WugBot v" + __version__)

    # Update the transcluded list of the 5 oldest noms
    links = []
    for ent in oldTen:
        links.append(ent.link(length=False, num=False))
    pText = "\n&bull; ".join(links[:5])
    pText += (
        "\n<!-- If you clear an item from backlog and want to update "
        + "the list before the bot next runs, here are the next "
        + "5 oldest nominations:\n&bull; "
    )
    pText += "\n&bull; ".join(links[5:])
    pText += "\n-->"
    if live == 0:
        pass
    elif live == 1:
        page = pywikibot.Page(site, "Wikipedia:Good article nominations/backlog/items")
        page.text = pText
        page.save("Updating list of oldest noms. WugBot v%s" % __version__)
    else:
        page = pywikibot.Page(site, "User:Wugapodes/GANReportBotTest/items")
        page.text = pText
        page.save("Testing WugBot v%s" % __version__)


def main():
    global live
    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, "Wikipedia:Good article nominations")
    nomPage = NomPage(page.text)
    nomPage.parse()
    report = nomPage.write_report()
    oldLine = nomPage.oldLine
    oldTen = nomPage.oldestTen
    save_pages(site, report, oldLine, oldTen)


if __name__ == "__main__":
    main()
    for i in range(1, len(sys.argv)):
        checkArgs(sys.argv[i])
