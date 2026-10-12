"""python manage.py import_gan_snapshot OLDID"""
from datetime import datetime, timezone

import pywikibot
from django.core.management.base import BaseCommand
from nominations.importer import import_snapshot

from ganreport.NomPage import NomPage


class Command(BaseCommand):
    help = "Import one historical revision of Wikipedia:Good article nominations"

    def add_arguments(self, parser):
        parser.add_argument("oldid", type=int)

    def handle(self, *args, **options):
        oldid = options["oldid"]
        site = pywikibot.Site("en", "wikipedia")
        page = pywikibot.Page(site, "Wikipedia:Good article nominations")
        revision = page.get_revision(oldid, content=True)
        timestamp = revision.timestamp
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        # Convert to naive UTC, then construct a *built-in* datetime.
        # Pywikibot Timestamp subclasses datetime and overrides formatting;
        # calling replace() alone can preserve that subclass.
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc)
        timestamp = datetime(
            timestamp.year,
            timestamp.month,
            timestamp.day,
            timestamp.hour,
            timestamp.minute,
            timestamp.second,
            timestamp.microsecond,
        )
        nompage = NomPage(revision.text)
        nompage.parse(organize=False, noms=False)
        snapshot = import_snapshot(
            nompage,
            revision_id=revision.revid,
            revision_timestamp=timestamp,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Revision {snapshot.revision_id}: "
                f"{snapshot.nominations.count()} nomination records"
            )
        )
