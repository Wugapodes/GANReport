"""Read-only analysis helpers for historical WP:GAN snapshots.

Run from ``python manage.py shell``::

    from nominations.analysis import snapshot_stats, snapshot_deltas, compare_snapshots
    rows = list(snapshot_stats())
    for row in rows:
        print(row.revision_timestamp.date(), row.total, row.under_review)
    for delta in snapshot_deltas():
        print(delta)
    print(compare_snapshots(rows[-2], rows[-1]))

All counts exclude malformed nominations. A status comparison uses the
(title, nomination_timestamp) pair as a *provisional* identity; it excludes
ambiguous duplicate keys rather than silently overwriting them.
"""

from collections import defaultdict

from django.db.models import Count, Q

from .models import Snapshot

STATUS_NAMES = {
    "U": "unreviewed",
    "R": "under_review",
    "H": "on_hold",
    "2": "second_opinion",
}
COUNT_FIELDS = ("total", *STATUS_NAMES.values())


def snapshot_stats():
    """Return snapshots in chronological order, annotated with status counts.

    This returns a lazy QuerySet. Each count excludes malformed nominations;
    ``total`` includes all non-malformed statuses, including unexpected ones.
    """
    valid = Q(nominations__malformed=False)
    annotations = {"total": Count("nominations", filter=valid)}
    for status, label in STATUS_NAMES.items():
        annotations[label] = Count(
            "nominations",
            filter=valid & Q(nominations__status=status),
        )
    return Snapshot.objects.annotate(**annotations).order_by("revision_timestamp", "pk")


def snapshot_deltas(snapshots=None):
    """Return per-snapshot counts and net changes from the preceding snapshot.

    Each result is a dict with ``revision_id``, ``timestamp``, ``counts``,
    and ``changes``. The first snapshot has ``changes=None``.
    """
    if snapshots is None:
        snapshots = snapshot_stats()

    result = []
    previous = None
    for snapshot in snapshots:
        counts = {field: getattr(snapshot, field) for field in COUNT_FIELDS}
        result.append(
            {
                "revision_id": snapshot.revision_id,
                "timestamp": snapshot.revision_timestamp,
                "counts": counts,
                "changes": (
                    {field: counts[field] - previous[field] for field in COUNT_FIELDS}
                    if previous is not None
                    else None
                ),
            }
        )
        previous = counts
    return result


def compare_snapshots(earlier, later):
    """Compare nominations between two Snapshot instances.

    Returns keys ``added``, ``removed``, ``status_changes``, and ``ambiguous``.
    The identity key (title, nomination_timestamp) is only provisional.
    Ambiguous keys, including duplicates within either snapshot or missing
    identity fields, are excluded from added/removed/status comparisons.
    """

    def grouped(snapshot):
        entries = defaultdict(list)
        incomplete = []
        for record in snapshot.nominations.filter(malformed=False):
            if not record.title or record.nomination_timestamp is None:
                incomplete.append(record)
                continue
            entries[(record.title, record.nomination_timestamp)].append(record)
        return entries, incomplete

    before, incomplete_before = grouped(earlier)
    after, incomplete_after = grouped(later)
    keys = set(before) | set(after)
    ambiguous = sorted(
        (
            key
            for key in keys
            if len(before.get(key, ())) > 1 or len(after.get(key, ())) > 1
        ),
        key=str,
    )
    safe = keys - set(ambiguous)

    added = [after[key][0] for key in safe if key not in before]
    removed = [before[key][0] for key in safe if key not in after]
    status_changes = [
        (before[key][0], after[key][0])
        for key in safe & set(before) & set(after)
        if before[key][0].status != after[key][0].status
    ]

    return {
        "added": sorted(added, key=lambda r: (r.title, r.position)),
        "removed": sorted(removed, key=lambda r: (r.title, r.position)),
        "status_changes": sorted(status_changes, key=lambda pair: pair[0].title),
        "ambiguous": ambiguous,
        "incomplete_before": incomplete_before,
        "incomplete_after": incomplete_after,
    }
