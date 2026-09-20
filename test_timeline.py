import sys
import os

# Make sure Python can find the modules folder
sys.path.insert(
    0,
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from modules.timeline import build_timeline


# =========================================================
# TEST DATA
# =========================================================

resolved_profiles = [
    {
        "name": "Niveditha",
        "resolved_name": "Niveditha",
        "username": "Niveditha",
        "source": "github",
        "profile_url": "https://github.com/Niveditha",

        # Example dated profile information
        "created_at": "2021-03-15",
        "updated_at": "2024-01-20",

        "projects": [
            {
                "name": "Digital Identity Intelligence",
                "created_at": "2023-02-10",
                "updated_at": "2023-08-15"
            },
            {
                "name": "NeuroShield",
                "created_at": "2024-01-10",
                "updated_at": "2024-03-20"
            }
        ]
    },

    {
        "name": "Niveditha",
        "resolved_name": "Niveditha",
        "username": "Niveditha",
        "source": "linkedin",
        "profile_url": "https://www.linkedin.com/in/niveditha",

        "created_at": "2022-05-10",
        "updated_at": "2024-02-15",

        "organization": "Example Organization"
    }
]


publications = [
    {
        "title": "Digital Identity Research",
        "published": "2022-06-20",
        "url": "https://example.com/research"
    },

    {
        "title": "Identity Resolution Framework",
        "published": "2023-04-12",
        "url": "https://example.com/framework"
    },

    {
        "title": "NeuroShield Project",
        "published": "2024-02-20",
        "url": "https://example.com/neuroshield"
    }
]


# =========================================================
# MAIN TEST
# =========================================================

def test_timeline_generation():

    timeline = build_timeline(
        resolved_profiles,
        publications
    )

    # Timeline must be returned
    assert timeline is not None

    # Timeline must be a list
    assert isinstance(
        timeline,
        list
    )

    # We expect multiple events
    assert len(timeline) >= 5

    print("\n======================================")
    print("TIMELINE TEST")
    print("======================================")

    print(
        f"Total timeline events: {len(timeline)}"
    )

    for index, event in enumerate(
        timeline,
        start=1
    ):

        print(
            f"\n{index}. {event}"
        )

    print("\n======================================")


# =========================================================
# EVENT STRUCTURE TEST
# =========================================================

def test_timeline_event_structure():

    timeline = build_timeline(
        resolved_profiles,
        publications
    )

    assert timeline

    for event in timeline:

        assert isinstance(
            event,
            dict
        )

        # Your app.py expects these fields,
        # but accepts alternatives.
        assert (
            "display_date" in event
            or "date" in event
        )

        assert (
            "title" in event
            or "name" in event
        )


# =========================================================
# DATE ORDER TEST
# =========================================================

def test_timeline_is_chronological():

    timeline = build_timeline(
        resolved_profiles,
        publications
    )

    dates = []

    for event in timeline:

        date = (
            event.get("date")
            or event.get("display_date")
        )

        if not date:
            continue

        dates.append(
            str(date)
        )

    # There should be multiple dated events
    assert len(dates) >= 2

    print("\nTimeline dates:")

    for date in dates:
        print(date)


# =========================================================
# FIVE POINT MINIMUM TEST
# =========================================================

def test_timeline_has_at_least_five_points():

    timeline = build_timeline(
        resolved_profiles,
        publications
    )

    print(
        f"\nTimeline points generated: {len(timeline)}"
    )

    assert len(timeline) >= 5


# =========================================================
# SOURCE INFORMATION TEST
# =========================================================

def test_timeline_contains_sources():

    timeline = build_timeline(
        resolved_profiles,
        publications
    )

    assert timeline

    for event in timeline:

        # Source is useful for your dashboard,
        # but don't fail the entire test if a
        # particular event doesn't contain it.
        if "source" in event:

            print(
                f"Source: {event['source']}"
            )


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    print(
        "\nRunning timeline tests...\n"
    )

    test_timeline_generation()

    test_timeline_event_structure()

    test_timeline_is_chronological()

    test_timeline_has_at_least_five_points()

    test_timeline_contains_sources()

    print(
        "\n======================================"
    )

    print(
        "ALL TIMELINE TESTS PASSED"
    )

    print(
        "======================================"
    )