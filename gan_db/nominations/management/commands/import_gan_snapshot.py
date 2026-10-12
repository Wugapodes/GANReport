"""python manage.py import_gan_snapshot OLDID"""

import pywikibot
from django.core.management.base import BaseCommand
from nominations.importer import import_snapshot

from ganreport.NomPage import NomPage
from ganreport.utils import normalize_timestamp


class Command(BaseCommand):
    help = "Import one historical revision of Wikipedia:Good article nominations"

    def add_arguments(self, parser):
        parser.add_argument("oldid", type=int)

    def handle(self, *args, **options):
        oldid = options["oldid"]
        site = pywikibot.Site("en", "wikipedia")
        page = pywikibot.Page(site, "Wikipedia:Good article nominations")
        revision = page.get_revision(oldid, content=True)
        timestamp = normalize_timestamp(revision.timestamp)
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
