import pytest

import ganreport.utils as utils


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param(
            "#:{{GAReview}} (2 reviews, 1 GA) "
            "[[User:Hason-LEK-SIN|Hason-LEK-SIN]] "
            "([[User talk:Hason-LEK-SIN|talk]]) "
            "08:31, 5 September 2026 (UTC)",
            ("Hason-LEK-SIN", "08:31, 5 September 2026"),
            id="default-template-hyphenated-username",
        ),
        pytest.param(
            "#:{{GAReview}} (101 reviews, 54 GAs) "
            "[[User:A.Cython|A.Cython]] "
            "([[User talk:A.Cython|talk]]) "
            "23:09, 19 September 2026 (UTC)",
            ("A.Cython", "23:09, 19 September 2026"),
            id="username-with-period",
        ),
        pytest.param(
            "#:{{GAReview}} (158 reviews, 62 GAs) "
            "[[User:It is a wonderful world|It is a wonderful world]] "
            "([[User talk:It is a wonderful world|talk]]) "
            "23:06, 20 July 2026 (UTC)",
            ("It is a wonderful world", "23:06, 20 July 2026"),
            id="username-with-multiple-spaces",
        ),
        pytest.param(
            "#:{{GAReview|status=on hold}} (11 reviews, 2 GAs) "
            "[[User:GRuban|GRuban]] "
            "([[User talk:GRuban|talk]]) "
            "16:24, 16 September 2026 (UTC)",
            ("GRuban", "16:24, 16 September 2026"),
            id="status-on-hold",
        ),
        pytest.param(
            "#:{{GAReview|status=2nd opinion}} (1 review, 0 GAs) "
            "[[User:Tioseafj|Tioseafj]] "
            "([[User talk:Tioseafj|talk]]) "
            "17:43, 9 May 2026 (UTC)",
            ("Tioseafj", "17:43, 9 May 2026"),
            id="status-second-opinion",
        ),
        pytest.param(
            "#:{{GAReview|status=on hold}} (50 reviews, 48 GAs) "
            "[[User:Vigilantcosmicpenguin|Vigilantcosmicpenguin]] "
            "([[User talk:Vigilantcosmicpenguin|talk]]) "
            "02:42, 27 September 2026 (UTC)",
            ("Vigilantcosmicpenguin", "02:42, 27 September 2026"),
            id="long-username",
        ),
        pytest.param(
            "#:{{GAReview}} (3 reviews, 1 GA) "
            "[[User:NRP|NRP]] ([[User talk:NRP|talk]]) "
            "21:42, 9 October 2026 (UTC)",
            ("NRP", "21:42, 9 October 2026"),
            id="short-username",
        ),
        pytest.param(
            "#:{{GAReview|status=on hold}} (1 review, 1 GA) "
            "[[User:NoahRiffe|NoahRiffe]] "
            "([[User talk:NoahRiffe|talk]]) "
            "00:01, 27 September 2026 (UTC)",
            ("NoahRiffe", "00:01, 27 September 2026"),
            id="time-just-after-midnight",
        ),
        pytest.param(
            "#:{{GAReview}} (1 review, 0 GAs) "
            "[[User:Fengrímur|Fengrímur]] "
            "([[User talk:Fengrímur|talk]]) "
            "12:34, 1 January 2026 (UTC)",
            ("Fengrímur", "12:34, 1 January 2026"),
            id="unicode-accented-username",
        ),
        pytest.param(
            "#:{{GAReview}} (0 reviews, 0 GAs) "
            "[[User:李明|李明]] ([[User talk:李明|talk]]) "
            "23:59, 31 December 2025 (UTC)",
            ("李明", "23:59, 31 December 2025"),
            id="unicode-cjk-username-end-of-year",
        ),
        pytest.param(
            "#:{{GAReview}} (0 reviews, 0 GAs) "
            "[[User:مثال|مثال]] ([[User talk:مثال|talk]]) "
            "00:00, 1 January 2026 (UTC)",
            ("مثال", "00:00, 1 January 2026"),
            id="unicode-arabic-username",
        ),
        pytest.param(
            "#:{{GAReview}} (0 reviews, 0 GAs) "
            "[[User:Example|Example]] "
            "([[User talk:Example|talk]]) "
            "12:00, 29 February 2024 (UTC)",
            ("Example", "12:00, 29 February 2024"),
            id="leap-day",
        ),
        pytest.param(
            "#:{{GAReview}} (0 reviews, 0 GAs) "
            "[[User:Example|Example]] "
            "([[User talk:Example|talk]]) Unknown timestamp",
            None,
            id="unknown-timestamp-standard-template",
        ),
        pytest.param(
            "# {{GANentry|1=Example|2=1}} "
            "[[User:Example|Example]] "
            "12:00, 1 January 2026 (UTC)",
            None,
            id="nomination-is-not-a-review",
        ),
        # Historical regressions
        # From Oct 2026
        pytest.param(
            "#:{{GAReview|status=2nd opinion}} (1 review, 0 GAs) "
            "[[User:White Rivers|White Rivers]] "
            "([[User talk:White Rivers|talk]]) Unknown timestamp",
            None,
            id="historical-unknown-timestamp",
        ),
    ],
)
def test_reviewRegex(text, expected):
    match = utils.reviewRegex.search(text)
    actual = match.groups() if match else None
    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param(
            "# {{GANentry|1=Tulip Shop Tavern|2=1"
            "|shortdesc=Restaurant in Portland, Oregon, U.S.}} "
            "(0 reviews, 217 GAs) "
            "[[User:Another Believer|Another Believer]] "
            "([[User talk:Another Believer|talk]]) "
            "18:04, 9 September 2026 (UTC)",
            (
                "Tulip Shop Tavern",
                "1",
                "(0 reviews, 217 GAs) "
                "[[User:Another Believer|Another Believer]] "
                "([[User talk:Another Believer|talk]])",
                "18:04, 9 September 2026",
            ),
            id="standard-entry",
        ),
        pytest.param(
            "# {{GANentry|1=Bell Labs Holmdel Complex|2=2"
            "|shortdesc=Mixed-use commercial complex in Holmdel, "
            "New Jersey|exists=yes}} "
            "(0 reviews, 0 GAs) "
            "[[User:MiracleMiles|MiracleMiles]] "
            "([[User talk:MiracleMiles|talk]]) "
            "01:32, 16 December 2025 (UTC)",
            (
                "Bell Labs Holmdel Complex",
                "2",
                "(0 reviews, 0 GAs) "
                "[[User:MiracleMiles|MiracleMiles]] "
                "([[User talk:MiracleMiles|talk]])",
                "01:32, 16 December 2025",
            ),
            id="type-2-with-exists",
        ),
        pytest.param(
            "# {{GANentry|1=Meditation (Maryon)|2=1"
            "|shortdesc=|exists=yes}} "
            "(151 reviews, 51 GAs) "
            "[[User:Usernameunique|Usernameunique]] "
            "([[User talk:Usernameunique|talk]]) "
            "19:58, 16 April 2026 (UTC)",
            (
                "Meditation (Maryon)",
                "1",
                "(151 reviews, 51 GAs) "
                "[[User:Usernameunique|Usernameunique]] "
                "([[User talk:Usernameunique|talk]])",
                "19:58, 16 April 2026",
            ),
            id="empty-shortdesc",
        ),
        pytest.param(
            "# {{GANentry|1=IG Farben Building|2=1"
            "|shortdesc=Building complex of Goethe University "
            "Frankfurt, Germany}} "
            "(0 reviews, 0 GAs) "
            "[[User:Fengrímur|Fengrímur]] "
            "([[User talk:Fengrímur|talk]]) "
            "11:59, 20 September 2026 (UTC)",
            (
                "IG Farben Building",
                "1",
                "(0 reviews, 0 GAs) "
                "[[User:Fengrímur|Fengrímur]] "
                "([[User talk:Fengrímur|talk]])",
                "11:59, 20 September 2026",
            ),
            id="unicode-username",
        ),
        pytest.param(
            "# {{GANentry|1=Lotus Temple|2=1"
            "|shortdesc=Baháʼí House of Worship in New Delhi, "
            "India, dedicated in December 1986|exists=yes}} "
            "(12 reviews, 2 GAs) "
            "[[User:ABehjat|ABehjat]] "
            "([[User talk:ABehjat|talk]]) "
            "23:17, 20 September 2026 (UTC)",
            (
                "Lotus Temple",
                "1",
                "(12 reviews, 2 GAs) "
                "[[User:ABehjat|ABehjat]] "
                "([[User talk:ABehjat|talk]])",
                "23:17, 20 September 2026",
            ),
            id="unicode-shortdesc",
        ),
        pytest.param(
            "# {{GANentry|1=Wooshkeetaan Kootéeyaa and "
            "Áakʼw Kootéeyaa|2=1"
            "|shortdesc=Pair of totem poles in Juneau, Alaska}} "
            "(2 reviews, 3 GAs) "
            "[[User:GreenLipstickLesbian|GreenLipstickLesbian]] "
            "([[User talk:GreenLipstickLesbian|talk]]) "
            "06:05, 5 October 2026 (UTC)",
            (
                "Wooshkeetaan Kootéeyaa and Áakʼw Kootéeyaa",
                "1",
                "(2 reviews, 3 GAs) "
                "[[User:GreenLipstickLesbian|GreenLipstickLesbian]] "
                "([[User talk:GreenLipstickLesbian|talk]])",
                "06:05, 5 October 2026",
            ),
            id="unicode-article-title",
        ),
        pytest.param(
            "# {{GANentry|1=1937–1938 Elgin Marbles cleaning "
            "scandal|2=1|shortdesc=none|exists=yes}} "
            "(69 reviews, 64 GAs) "
            "[[User:UndercoverClassicist|UndercoverClassicist]] "
            "([[User talk:UndercoverClassicist|talk]]) "
            "06:32, 1 October 2026 (UTC)",
            (
                "1937–1938 Elgin Marbles cleaning scandal",
                "1",
                "(69 reviews, 64 GAs) "
                "[[User:UndercoverClassicist|UndercoverClassicist]] "
                "([[User talk:UndercoverClassicist|talk]])",
                "06:32, 1 October 2026",
            ),
            id="en-dash-title-and-none-shortdesc",
        ),
        # Synthetic edge cases
        pytest.param(
            "# {{GANentry|1=Example article|2=1|shortdesc=Example}} "
            "(0 reviews, 0 GAs) "
            "[[User:李明|李明]] ([[User talk:李明|talk]]) "
            "00:00, 1 January 2026 (UTC)",
            (
                "Example article",
                "1",
                "(0 reviews, 0 GAs) " "[[User:李明|李明]] ([[User talk:李明|talk]])",
                "00:00, 1 January 2026",
            ),
            id="cjk-username-midnight",
        ),
        pytest.param(
            "# {{GANentry|1=Example article|2=1}} "
            "(0 reviews, 0 GAs) "
            "[[User:Example|Example]] "
            "([[User talk:Example|talk]]) "
            "23:59, 29 February 2024 (UTC)",
            (
                "Example article",
                "1",
                "(0 reviews, 0 GAs) "
                "[[User:Example|Example]] "
                "([[User talk:Example|talk]])",
                "23:59, 29 February 2024",
            ),
            id="no-extra-parameters-leap-day",
        ),
        pytest.param(
            "# {{GANentry|1=Example article|2=1}} "
            "(0 reviews, 0 GAs) "
            "[[User:Example|Example]] "
            "([[User talk:Example|talk]]) Unknown timestamp",
            None,
            id="unknown-timestamp",
        ),
        pytest.param(
            "#:{{GAReview}} (1 review, 0 GAs) "
            "[[User:Example|Example]] "
            "([[User talk:Example|talk]]) "
            "12:00, 1 January 2026 (UTC)",
            None,
            id="review-is-not-nomination",
        ),
    ],
)
def test_entRegex(text, expected):
    match = utils.entRegex.search(text)
    actual = match.groups() if match else None
    assert actual == expected
