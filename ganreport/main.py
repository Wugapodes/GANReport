#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import argparse
import logging

import pywikibot

from ganreport.NomPage import NomPage

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


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

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Set logging level to DEBUG"
    )
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


if __name__ == "__main__":
    main()
