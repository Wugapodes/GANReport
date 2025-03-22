#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Produceds a report on English Wikipedia's Good Article Project Backlog"""

import argparse

import pywikibot

from ganreport.NomPage import NomPage

__author__ = "Wugapodes"
__copyright__ = "Copyright 2019-2025, Wugapodes"
__license__ = "MIT"
__version__ = "3.0.0-dev"
__maintainer__ = "Wugapodes"
__email__ = "wugapodes@gmail.com"
__status__ = "Development"


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
    parser = argparse.ArgumentParser(description="Good Article Nomination Report")
    parser.add_argument(
        "--write_mode",
        choices=["live", "sandbox", "dryrun"],
        default="dryrun",
        help="If 'live' write the report. If 'sandbox' write to a user page. If 'dryrun' generate the report but do not write to the wiki.",
    )

    args = parser.parse_args()

    write_mode = args.write_mode
    if write_mode == "dryrun":
        live = 0
    elif write_mode == "live":
        live = 1
    else:
        live = -1

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
