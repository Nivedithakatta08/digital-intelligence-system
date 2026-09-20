
from datetime import datetime


# =========================================================
# DATE PARSING
# =========================================================

def parse_date(value):

    if not value:
        return None

    text = str(value).strip()

    if not text:
        return None

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m",
        "%Y/%m",
        "%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                text,
                fmt
            )

        except ValueError:

            continue

    # Handle ISO timestamps such as:
    # 2025-09-20T14:30:00+00:00
    try:

        return datetime.fromisoformat(
            text.replace(
                "Z",
                "+00:00"
            )
        ).replace(
            tzinfo=None
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# =========================================================
# DATE FORMATTING
# =========================================================

def format_date(value):

    parsed = parse_date(
        value
    )

    if parsed is None:

        return (
            str(value)
            if value
            else "Date unavailable"
        )

    text = str(
        value
    ).strip()

    # Year
    if (
        len(text) == 4
        and text.isdigit()
    ):

        return parsed.strftime(
            "%Y"
        )

    # Year + month
    if len(text) == 7:

        return parsed.strftime(
            "%B %Y"
        )

    return parsed.strftime(
        "%d %B %Y"
    )


# =========================================================
# ADD TIMELINE EVENT
# =========================================================

def add_event(
    events,
    date,
    event_type,
    title,
    source="",
    details="",
    url="",
    confidence=None
):

    if not date:

        return

    parsed = parse_date(
        date
    )

    # We don't add records that cannot be ordered.
    if parsed is None:

        return

    events.append(
        {
            "date": str(date),
            "display_date": format_date(
                date
            ),
            "event": (
                event_type
                or "Activity"
            ),
            "title": (
                title
                or event_type
                or "Identity activity"
            ),
            "source": (
                source
                or "Public source"
            ),
            "details": (
                details
                or ""
            ),
            "url": (
                url
                or ""
            ),
            "confidence": confidence,
            "_parsed_date": parsed
        }
    )


# =========================================================
# LIST HELPER
# =========================================================

def as_list(value):

    if value is None:

        return []

    if isinstance(
        value,
        list
    ):

        return value

    return [value]


# =========================================================
# SOURCE
# =========================================================

def get_source(profile):

    if not isinstance(
        profile,
        dict
    ):

        return "Public source"

    sources = profile.get(
        "sources"
    )

    if isinstance(
        sources,
        list
    ) and sources:

        return ", ".join(
            str(source)
            for source in sources
            if source
        )

    return (
        profile.get(
            "source"
        )
        or "Public source"
    )


# =========================================================
# PROFILE TIMELINE
# =========================================================

def extract_profile_events(
    profile,
    events
):

    if not isinstance(
        profile,
        dict
    ):

        return

    source = get_source(
        profile
    )

    # -----------------------------------------------------
    # EXPLICIT TIMELINE
    # -----------------------------------------------------

    timeline = profile.get(
        "timeline"
    )

    for item in as_list(
        timeline
    ):

        if not isinstance(
            item,
            dict
        ):

            continue

        date = (
            item.get("date")
            or item.get("year")
            or item.get("timestamp")
            or item.get("created")
        )

        if not date:

            continue

        add_event(
            events=events,
            date=date,
            event_type=(
                item.get(
                    "event"
                )
                or "Profile activity"
            ),
            title=(
                item.get(
                    "title"
                )
                or "Profile activity"
            ),
            source=(
                item.get(
                    "source"
                )
                or source
            ),
            details=(
                item.get(
                    "details"
                )
                or item.get(
                    "description",
                    ""
                )
            ),
            url=item.get(
                "url",
                ""
            ),
            confidence=item.get(
                "confidence"
            )
        )

    # -----------------------------------------------------
    # GITHUB CREATED DATE
    # -----------------------------------------------------

    created = (
        profile.get(
            "github_created_at"
        )
        or profile.get(
            "created_at"
        )
        or profile.get(
            "created"
        )
    )

    if created:

        add_event(
            events=events,
            date=created,
            event_type="Profile Created",
            title="Public profile created",
            source=source,
            details=(
                "The public profile creation date "
                "was available from the source."
            ),
            url=profile.get(
                "profile_url",
                ""
            ),
            confidence=0.90
        )

    # -----------------------------------------------------
    # PROFILE UPDATED DATE
    # -----------------------------------------------------

    updated = (
        profile.get(
            "github_updated_at"
        )
        or profile.get(
            "updated_at"
        )
        or profile.get(
            "updated"
        )
    )

    if updated:

        add_event(
            events=events,
            date=updated,
            event_type="Profile Updated",
            title="Public profile updated",
            source=source,
            details=(
                "The public profile update date "
                "was available from the source."
            ),
            url=profile.get(
                "profile_url",
                ""
            ),
            confidence=0.90
        )


# =========================================================
# PROJECTS
# =========================================================

def extract_projects(
    profile,
    events
):

    if not isinstance(
        profile,
        dict
    ):

        return

    source = get_source(
        profile
    )

    projects = profile.get(
        "projects"
    )

    for project in as_list(
        projects
    ):

        if isinstance(
            project,
            dict
        ):

            date = (
                project.get(
                    "date"
                )
                or project.get(
                    "start_date"
                )
                or project.get(
                    "created_at"
                )
                or project.get(
                    "year"
                )
            )

            title = (
                project.get(
                    "name"
                )
                or project.get(
                    "title"
                )
                or project.get(
                    "project"
                )
                or "Project"
            )

            details = (
                project.get(
                    "description"
                )
                or ""
            )

            url = (
                project.get(
                    "url"
                )
                or project.get(
                    "html_url"
                )
                or ""
            )

        else:

            # A project without a date is not placed
            # on the chronological timeline.
            date = None

            title = str(
                project
            )

            details = ""

            url = ""

        if not date:

            continue

        add_event(
            events=events,
            date=date,
            event_type="Project",
            title=title,
            source=source,
            details=details,
            url=url,
            confidence=0.90
        )


# =========================================================
# EVENTS
# =========================================================

def extract_events(
    profile,
    events
):

    if not isinstance(
        profile,
        dict
    ):

        return

    source = get_source(
        profile
    )

    activities = profile.get(
        "events"
    )

    for activity in as_list(
        activities
    ):

        if isinstance(
            activity,
            dict
        ):

            date = (
                activity.get(
                    "date"
                )
                or activity.get(
                    "start_date"
                )
                or activity.get(
                    "created_at"
                )
                or activity.get(
                    "year"
                )
            )

            title = (
                activity.get(
                    "name"
                )
                or activity.get(
                    "title"
                )
                or "Event"
            )

            details = (
                activity.get(
                    "description"
                )
                or ""
            )

            url = (
                activity.get(
                    "url"
                )
                or ""
            )

        else:

            date = None

            title = str(
                activity
            )

            details = ""

            url = ""

        if not date:

            continue

        add_event(
            events=events,
            date=date,
            event_type="Event",
            title=title,
            source=source,
            details=details,
            url=url,
            confidence=0.90
        )


# =========================================================
# PUBLICATIONS
# =========================================================

def extract_publications(
    publications,
    events
):

    for publication in publications or []:

        if not isinstance(
            publication,
            dict
        ):

            continue

        published = (
            publication.get(
                "published"
            )
            or publication.get(
                "published_date"
            )
            or publication.get(
                "publication_date"
            )
            or publication.get(
                "date"
            )
            or publication.get(
                "created"
            )
        )

        if not published:

            continue

        title = (
            publication.get(
                "title"
            )
            or "Untitled publication"
        )

        doi = publication.get(
            "doi"
        )

        url = publication.get(
            "url"
        )

        if not url and doi:

            doi_text = str(
                doi
            ).strip()

            if doi_text.startswith(
                "http"
            ):

                url = doi_text

            else:

                url = (
                    "https://doi.org/"
                    + doi_text
                )

        authors = publication.get(
            "authors",
            []
        )

        if isinstance(
            authors,
            list
        ):

            author_text = ", ".join(
                str(author)
                for author in authors
                if author
            )

        else:

            author_text = (
                str(authors)
                if authors
                else ""
            )

        details = ""

        if author_text:

            details = (
                "Authors: "
                + author_text
            )

        add_event(
            events=events,
            date=published,
            event_type="Publication",
            title=title,
            source="Crossref",
            details=details,
            url=url or "",
            confidence=0.90
        )


# =========================================================
# DEDUPLICATION
# =========================================================

def deduplicate_events(
    events
):

    unique = []

    seen = set()

    for event in events:

        if not isinstance(
            event,
            dict
        ):

            continue

        key = (
            str(
                event.get(
                    "date",
                    ""
                )
            ).strip().lower(),

            str(
                event.get(
                    "event",
                    ""
                )
            ).strip().lower(),

            str(
                event.get(
                    "title",
                    ""
                )
            ).strip().lower()
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        unique.append(
            event
        )

    return unique


# =========================================================
# BUILD TIMELINE
# =========================================================

def build_timeline(
    profiles,
    publications=None
):

    if publications is None:

        publications = []

    events = []

    # -----------------------------------------------------
    # PROFILES
    # -----------------------------------------------------

    for profile in profiles or []:

        if not isinstance(
            profile,
            dict
        ):

            continue

        extract_profile_events(
            profile,
            events
        )

        extract_projects(
            profile,
            events
        )

        extract_events(
            profile,
            events
        )

    # -----------------------------------------------------
    # PUBLICATIONS
    # -----------------------------------------------------

    extract_publications(
        publications,
        events
    )

    # -----------------------------------------------------
    # DEDUPLICATE
    # -----------------------------------------------------

    events = deduplicate_events(
        events
    )

    # -----------------------------------------------------
    # SORT CHRONOLOGICALLY
    # -----------------------------------------------------

    events.sort(
        key=lambda event: event.get(
            "_parsed_date",
            datetime.max
        )
    )

    # -----------------------------------------------------
    # CLEAN INTERNAL DATE
    # -----------------------------------------------------

    for index, event in enumerate(
        events,
        start=1
    ):

        event["position"] = index

        event.pop(
            "_parsed_date",
            None
        )

    return events


# =========================================================
# TIMELINE SUMMARY
# =========================================================

def summarize_timeline(
    timeline
):

    if not isinstance(
        timeline,
        list
    ):

        timeline = []

    event_types = {}

    dates = []

    for event in timeline:

        if not isinstance(
            event,
            dict
        ):

            continue

        event_type = (
            event.get(
                "event"
            )
            or "Activity"
        )

        event_types[event_type] = (
            event_types.get(
                event_type,
                0
            )
            + 1
        )

        parsed = parse_date(
            event.get(
                "date"
            )
        )

        if parsed:

            dates.append(
                parsed
            )

    first_date = None
    latest_date = None

    if dates:

        first_date = min(
            dates
        ).strftime(
            "%d %B %Y"
        )

        latest_date = max(
            dates
        ).strftime(
            "%d %B %Y"
        )

    return {
        "total_events": len(
            timeline
        ),
        "event_types": event_types,
        "first_activity": first_date,
        "latest_activity": latest_date
    }
