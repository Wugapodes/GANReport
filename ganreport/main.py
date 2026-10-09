#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import argparse
import logging
from datetime import date, datetime, timedelta

import pywikibot

from ganreport.NomPage import NomPage
from ganreport.utils import timestamp_pattern, wiki2datetime

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"

log = logging.getLogger(__name__)


def save_pages(site, report, oldLine, oldTen, write_mode):
    page = pywikibot.Page(site, "Wikipedia:Good article nominations/Report")
    # Determine if the bot should write to a live page or the test page.
    if write_mode == "dry_run":
        pass
    elif write_mode == "prod":
        page.text = report
        page.save("Updating exceptions report, WugBot v" + __version__)
        page = pywikibot.Page(
            site, "Wikipedia:Good article nominations/Report/Backlog archive"
        )
        page.text += "\n" + oldLine
        page.save("Update of GAN report backlog, WugBot v" + __version__)
    elif write_mode == "sandbox":
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
    if write_mode == "dryrun":
        pass
    elif write_mode == "prod":
        page = pywikibot.Page(site, "Wikipedia:Good article nominations/backlog/items")
        page.text = pText
        page.save("Updating list of oldest noms. WugBot v%s" % __version__)
    elif write_mode == "sandbox":
        page = pywikibot.Page(site, "User:Wugapodes/GANReportBotTest/items")
        page.text = pText
        page.save("Testing WugBot v%s" % __version__)


def standard_args():
    parser = argparse.ArgumentParser(description="Good Article Nomination Report")
    parser.add_argument(
        "--write_mode",
        choices=["prod", "sandbox", "dryrun"],
        default="dryrun",
        help="If 'live' write the report. If 'sandbox' write to a user page. If 'dryrun' generate the report but do not write to the wiki.",
    )

    parser.add_argument(
        "--archive_path",
        default="/data/project/ganreportbot/",
        help="Path which contains the backlog_report.txt and beta_backlog_report.txt",
    )

    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def main():
    parser = standard_args()
    args = parser.parse_args()

    logging.basicConfig(
        filename="GANReportBot.log"
        if args.write_mode == "prod"
        else "Test.GANReportBot.log",
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )

    write_mode = args.write_mode
    archive_path = args.archive_path

    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, "Wikipedia:Good article nominations")
    nomPage = NomPage(page.text)
    nomPage.parse()
    report = nomPage.write_report(write_mode, archive_path)
    oldLine = nomPage.oldLine
    oldTen = nomPage.oldestTen
    save_pages(site, report, oldLine, oldTen, write_mode)


def fix_gaps():
    parser = standard_args()

    parser.add_argument(
        "--start_date",
        type=date.fromisoformat,
        help="Start date (YYY-MM-DD), default is May 9, 2007",
        default=date(2007, 5, 9),
    )

    parser.add_argument(
        "--end_date",
        type=date.fromisoformat,
        help="End date (YYY-MM-DD), default is today",
        default=date.today(),
    )

    args = parser.parse_args()

    logging.basicConfig(
        filename="FixGANReportGaps.log"
        if args.write_mode == "prod"
        else "Test.FixGANReportGaps.log",
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )

    # write_mode = args.write_mode
    archive_path = args.archive_path

    start_date = args.start_date
    end_date = args.end_date

    find_archive_gaps(start_date, end_date, archive_path)


def find_archive_gaps(start, end, archive_path):
    def get_archive_page(year):
        site = pywikibot.Site("en", "wikipedia")
        archive_stem = "Wikipedia:Good_article_nominations/Report/Backlog_archive/"
        archive_page = pywikibot.Page(site, archive_stem + str(year_cursor))
        return archive_page

    year_cursor = start.year
    date_cursor = start
    gap_list = []
    for year_cursor in range(start.year, end.year + 1):
        archive_page = get_archive_page(start.year)
        for line in archive_page.text.splitlines():
            match = timestamp_pattern.match(line)
            if match:
                entry_dt = wiki2datetime(match.group(1))
                if entry_dt.date() >= start:
                    if entry_dt.date() >= end:
                        # What if there's an ongoing gap? 10-9-2026
                        break
                    date_diff = entry_dt.date() - date_cursor
                    if date_diff == 0:
                        continue
                    elif date_diff.days > 1:
                        log.debug(f"Gap! {date_cursor} to {entry_dt.date()}")
                        gap_list.append(
                            [
                                date_cursor + timedelta(days=1),
                                entry_dt.date() - timedelta(days=1),
                            ]
                        )
                    date_cursor = entry_dt.date()
    log.debug(gap_list)
    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, "Wikipedia:Good article nominations")
    for gap in gap_list:
        for i in range((gap[1] - gap[0]).days + 1):
            log.debug(gap)
            d = gap[0] + timedelta(days=i)
            dt = datetime(d.year, d.month, d.day, 13, 51)
            log.debug(dt)
            old_nominations = next(page.revisions(starttime=dt, total=1), None)
            if old_nominations:
                oldid = old_nominations.revid
                log.debug(oldid)
                old_page = page.get_revision(oldid, content=True)
                oldNomPage = NomPage(old_page.text)
                oldNomPage.parse()
                # Use the dt to avoid keeping gaps on days with no changes
                # Normal runs are timestamped from the run, not the revision they used
                # Marks gap fills with 13:51 ("test") so they're a little more obvious
                log.debug(oldNomPage.print_backlog_report_line(dt))


if __name__ == "__main__":
    main()
