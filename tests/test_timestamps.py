from datetime import datetime

import pytest

# Replace with your actual module
from ganreport.utils import wiki2datetime, wikiTimeStamp


@pytest.mark.parametrize(
    "timestamp, expected",
    [
        pytest.param(
            "06:47, 16 May 2007 (UTC)",
            datetime(2007, 5, 16, 6, 47),
            id="standard-timestamp",
        ),
        pytest.param(
            "17:12, 20 December 2023",
            datetime(2023, 12, 20, 17, 12),
            id="without-utc-suffix",
        ),
        pytest.param(
            "00:00, 1 January 2024 (UTC)",
            datetime(2024, 1, 1, 0, 0),
            id="midnight-single-digit-day",
        ),
        pytest.param(
            "23:59, 31 December 2023 (UTC)",
            datetime(2023, 12, 31, 23, 59),
            id="end-of-year",
        ),
        pytest.param(
            "12:30, 29 February 2024 (UTC)",
            datetime(2024, 2, 29, 12, 30),
            id="leap-day",
        ),
        pytest.param(
            "09:05, 9 September 2009 (UTC)",
            datetime(2009, 9, 9, 9, 5),
            id="single-digit-day-and-minute",
        ),
        pytest.param(
            "01:02, 1 March 2001",
            datetime(2001, 3, 1, 1, 2),
            id="early-year-without-suffix",
        ),
    ],
)
def test_wiki2datetime(timestamp, expected):
    assert wiki2datetime(timestamp) == expected


@pytest.mark.parametrize(
    "timestamp",
    [
        "Unknown timestamp",
        "",
        "not a date",
        "25:00, 1 January 2024 (UTC)",
        "12:60, 1 January 2024 (UTC)",
        "12:00, 32 January 2024 (UTC)",
        "12:00, 29 February 2023 (UTC)",
        "12:00, 1 NotAMonth 2024 (UTC)",
    ],
)
def test_wiki2datetime_invalid(timestamp):
    with pytest.raises(ValueError):
        wiki2datetime(timestamp)


def test_wikiTimeStamp_format():
    """The result should be a valid Wikipedia UTC timestamp."""
    timestamp = wikiTimeStamp()

    assert timestamp.endswith(" (UTC)")

    parsed = wiki2datetime(timestamp)
    assert isinstance(parsed, datetime)
    assert parsed.tzinfo is None


def test_wikiTimeStamp_accuracy():
    """The timestamp should represent the current UTC minute."""
    before = datetime.utcnow()
    timestamp = wikiTimeStamp()
    after = datetime.utcnow()

    parsed = wiki2datetime(timestamp)

    assert (
        before.replace(second=0, microsecond=0)
        <= parsed
        <= after.replace(second=0, microsecond=0)
    )


def test_wikiTimeStamp_day_format():
    """Wikipedia signatures should not zero-pad the day."""
    timestamp = wikiTimeStamp()
    parsed = wiki2datetime(timestamp)

    expected = (
        parsed.strftime("%H:%M, ") + str(parsed.day) + parsed.strftime(" %B %Y (UTC)")
    )

    assert timestamp == expected


def test_wikiTimeStamp_roundtrip():
    """The generated timestamp should parse into a naive datetime."""
    timestamp = wikiTimeStamp()
    parsed = wiki2datetime(timestamp)

    assert isinstance(parsed, datetime)
    assert parsed.tzinfo is None
    assert parsed.second == 0
    assert parsed.microsecond == 0
