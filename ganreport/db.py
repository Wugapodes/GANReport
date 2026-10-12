import os
import sys
from pathlib import Path

from ganreport.utils import normalize_timestamp


def save_snapshot(nompage, revision):
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "gan_db"))

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "ganweb.settings",
    )

    import django

    django.setup()

    from nominations.importer import import_snapshot

    return import_snapshot(
        nompage,
        revision_id=revision.revid,
        revision_timestamp=normalize_timestamp(revision.timestamp),
    )
