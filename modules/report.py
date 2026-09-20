import json
import os
from datetime import datetime


OUTPUT_DIR = "outputs"


# ============================================================
# HELPERS
# ============================================================

def safe_list(value):

    if value is None:
        return []

    if isinstance(
        value,
        list
    ):
        return value

    return [value]


def readable_value(value):

    values = safe_list(
        value
    )

    cleaned = [
        str(item)
        for item in values
        if item not in (
            None,
            ""
        )
    ]

    return cleaned


# ============================================================
# VIEWER PROFILE
# ============================================================

def create_viewer_profile(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return {}

    return {
        "Identity": (
            profile.get(
                "resolved_name"
            )
            or profile.get(
                "name"
            )
            or profile.get(
                "full_name"
            )
            or profile.get(
                "username"
            )
            or "Unknown"
        ),

        "Aliases": readable_value(
            profile.get(
                "aliases"
            )
        ),

        "Usernames": readable_value(
            profile.get(
                "usernames"
            )
            or profile.get(
                "username"
            )
        ),

        "Organizations": readable_value(
            profile.get(
                "organizations"
            )
            or profile.get(
                "organization"
            )
        ),

        "Roles": readable_value(
            profile.get(
                "roles"
            )
        ),

        "Projects": readable_value(
            profile.get(
                "projects"
            )
        ),

        "Events": readable_value(
            profile.get(
                "events"
            )
        ),

        "Locations": readable_value(
            profile.get(
                "locations"
            )
            or profile.get(
                "location"
            )
        ),

        "Sources": readable_value(
            profile.get(
                "sources"
            )
            or profile.get(
                "source"
            )
        ),

        "Confidence": profile.get(
            "confidence_percentage"
        ),

        "Confidence Level": profile.get(
            "confidence_label"
        ),

        "Profile URL": profile.get(
            "profile_url"
        )
    }


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report(
    profiles,
    evidence,
    conflicts,
    publications=None,
    timeline=None,
    intelligence=None,
    graph_path=None
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    profiles = (
        profiles
        if isinstance(
            profiles,
            list
        )
        else []
    )

    evidence = (
        evidence
        if isinstance(
            evidence,
            list
        )
        else []
    )

    conflicts = (
        conflicts
        if isinstance(
            conflicts,
            list
        )
        else []
    )

    publications = (
        publications
        if isinstance(
            publications,
            list
        )
        else []
    )

    timeline = (
        timeline
        if isinstance(
            timeline,
            list
        )
        else []
    )

    intelligence = (
        intelligence
        if isinstance(
            intelligence,
            list
        )
        else []
    )

    # --------------------------------------------------------
    # Readable profiles
    # --------------------------------------------------------

    readable_profiles = []

    for profile in profiles:

        readable = create_viewer_profile(
            profile
        )

        if readable:

            readable_profiles.append(
                readable
            )

    # --------------------------------------------------------
    # Best identity
    # --------------------------------------------------------

    best_identity = {}

    if profiles:

        best_identity = max(
            profiles,
            key=lambda profile:
            profile.get(
                "confidence",
                0.0
            )
        )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    report = {

        "system": {

            "name":
                "Digital Identity Intelligence System",

            "purpose":
                (
                    "Public-source identity resolution "
                    "using username or image-based "
                    "candidate identification, profile "
                    "discovery, identity resolution, "
                    "evidence analysis, conflict detection, "
                    "timeline construction and "
                    "high-confidence knowledge graph generation."
                ),

            "generated_at":
                datetime.now().isoformat()
        },

        "summary": {

            "profiles_found":
                len(profiles),

            "evidence_items":
                len(evidence),

            "conflicts_found":
                len(conflicts),

            "publications_found":
                len(publications),

            "timeline_events":
                len(timeline),

            "intelligence_items":
                len(intelligence),

            "graph_generated":
                bool(graph_path)
        },

        "best_identity":
            best_identity,

        "readable_profiles":
            readable_profiles,

        "profiles":
            profiles,

        "evidence":
            evidence,

        "conflicts":
            conflicts,

        "publications":
            publications,

        "timeline":
            timeline,

        "intelligence":
            intelligence,

        "knowledge_graph": {

            "generated":
                bool(graph_path),

            "path":
                graph_path,

            "confidence_threshold":
                0.75
        }
    }

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    report_path = os.path.join(
        OUTPUT_DIR,
        "report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return report