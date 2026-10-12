"""Bridge existing ganreport.NomPage parsing to Django persistence."""
from django.db import transaction

from .models import NominationRecord, Snapshot


def iter_entries(nompage):
    """Yield (section name, subsection name or None, Entry) in page order."""
    for section in nompage.section:
        for entry in section.entries:
            yield section.name, None, entry
        for subsection in section.subsections:
            if subsection is None:  # Miscellaneous's sentinel
                continue
            for entry in subsection.entries:
                yield section.name, subsection.name, entry


@transaction.atomic
def import_snapshot(nompage, revision_id, revision_timestamp):
    """Import a parsed NomPage once. Does not guess cross-revision identities.

    The caller should use nompage.parse(organize=False, noms=False), so that
    classification using datetime.utcnow() does not affect historical imports.
    """
    snapshot, created = Snapshot.objects.get_or_create(
        revision_id=revision_id,
        defaults={"revision_timestamp": revision_timestamp},
    )
    if not created:
        return snapshot

    records = []
    for position, (section, subsection, entry) in enumerate(iter_entries(nompage)):
        # Entry.add_review sets r_timestamp to CURRENT time if parsing fails.
        # Never store that synthetic value as historical evidence.
        review_ts = (
            entry.r_timestamp
            if entry.status is not None and not entry.badreview
            else None
        )
        records.append(
            NominationRecord(
                snapshot=snapshot,
                position=position,
                title=entry.title,
                nominator=entry.nominator,
                nomination_number=str(entry.number),
                nomination_timestamp=entry.timestamp,
                section=section,
                subsection=subsection,
                status=entry.status if entry.status is not None else "U",
                review_timestamp=review_ts,
                malformed=entry.bad,
                malformed_review=entry.badreview,
                raw_text=entry.text,
            )
        )
    NominationRecord.objects.bulk_create(records, batch_size=500)
    return snapshot
