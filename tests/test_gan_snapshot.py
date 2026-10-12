import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest
from nominations.importer import import_snapshot

from ganreport.NomPage import NomPage

FIXTURES = Path(__file__).parent / "fixtures"
OLDID = 1379796878


@pytest.mark.django_db
@pytest.mark.integration
def test_historical_snapshot_import():
    # Load fixed historical input and expected results
    text = (FIXTURES / f"gan_{OLDID}.txt").read_text(encoding="utf-8")
    expected = json.loads((FIXTURES / f"gan_{OLDID}.json").read_text(encoding="utf-8"))

    # Run production parser
    page = NomPage(text)
    page.parse(organize=False, noms=False)

    # Import into pytest's isolated test database
    snapshot = import_snapshot(
        page,
        revision_id=OLDID,
        revision_timestamp=datetime(2025, 1, 1),
    )

    records = list(snapshot.nominations.order_by("position"))

    # Aggregate assertions
    assert len(records) == expected["total"]

    counts = dict(Counter(r.status for r in records if not r.malformed))
    assert counts == expected["status_counts"]

    assert sum(r.malformed for r in records) == expected["malformed"]

    # Individual record assertions
    actual_records = [
        {
            "position": r.position,
            "title": r.title,
            "nominator": r.nominator,
            "status": r.status,
            "malformed": r.malformed,
            "malformed_review": r.malformed_review,
            "nomination_timestamp": (
                r.nomination_timestamp.isoformat() if r.nomination_timestamp else None
            ),
        }
        for r in records
    ]

    assert actual_records == expected["records"]
