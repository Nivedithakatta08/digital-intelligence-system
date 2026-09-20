# ============================================================
# HELPERS
# ============================================================

def as_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return [
            item for item in value
            if item not in (None, "")
        ]

    return [value]


def add_evidence(
    evidence,
    evidence_type,
    value,
    description,
    profile
):

    if value in (None, "", []):
        return

    if isinstance(value, list):

        value = ", ".join(
            str(item)
            for item in value
            if item
        )

    item = {
        "type": evidence_type,
        "value": str(value),
        "description": description
    }

    if isinstance(profile, dict):

        candidate_id = profile.get(
            "candidate_id"
        )

        source = profile.get(
            "source"
        )

        if candidate_id:
            item["candidate_id"] = candidate_id

        if source:
            item["source"] = source

    evidence.append(item)


# ============================================================
# CREATE EVIDENCE
# ============================================================

def create_evidence(profile):

    if not isinstance(
        profile,
        dict
    ):
        return []

    evidence = []

    source = profile.get(
        "source"
    )

    sources = profile.get(
        "sources"
    )

    name = (
        profile.get("name")
        or profile.get("full_name")
        or profile.get("display_name")
    )

    username = profile.get(
        "username"
    )

    usernames = profile.get(
        "usernames"
    )

    aliases = profile.get(
        "aliases"
    )

    organization = (
        profile.get("organization")
        or profile.get("organizations")
    )

    roles = profile.get(
        "roles"
    )

    projects = profile.get(
        "projects"
    )

    events = profile.get(
        "events"
    )

    location = (
        profile.get("location")
        or profile.get("locations")
    )

    profile_url = profile.get(
        "profile_url"
    )

    image_score = (
        profile.get("image_similarity")
        or profile.get("image_match_score")
    )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    if sources:

        add_evidence(
            evidence,
            "source",
            sources,
            "Information was found across these public sources.",
            profile
        )

    elif source:

        add_evidence(
            evidence,
            "source",
            source,
            f"Information was discovered from {source}.",
            profile
        )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    add_evidence(
        evidence,
        "name",
        name,
        "Publicly displayed identity name.",
        profile
    )

    add_evidence(
        evidence,
        "username",
        username,
        "Public account identifier.",
        profile
    )

    if usernames:

        add_evidence(
            evidence,
            "usernames",
            usernames,
            "Additional public usernames associated with the identity.",
            profile
        )

    if aliases:

        add_evidence(
            evidence,
            "aliases",
            aliases,
            "Alternative names or aliases associated with the identity.",
            profile
        )

    # --------------------------------------------------------
    # Associations
    # --------------------------------------------------------

    add_evidence(
        evidence,
        "organization",
        organization,
        "Publicly associated organization.",
        profile
    )

    add_evidence(
        evidence,
        "roles",
        roles,
        "Publicly associated roles.",
        profile
    )

    add_evidence(
        evidence,
        "projects",
        projects,
        "Publicly associated projects.",
        profile
    )

    add_evidence(
        evidence,
        "events",
        events,
        "Publicly associated events.",
        profile
    )

    add_evidence(
        evidence,
        "location",
        location,
        "Publicly displayed or associated location.",
        profile
    )

    # --------------------------------------------------------
    # Image evidence
    # --------------------------------------------------------

    if image_score is not None:

        try:

            score_value = float(
                image_score
            )

            if score_value > 1:
                score_value /= 100

            score_value = max(
                0.0,
                min(
                    score_value,
                    1.0
                )
            )

            add_evidence(
                evidence,
                "image_match",
                f"{score_value * 100:.1f}%",
                "Similarity score returned by the connected image identity provider.",
                profile
            )

        except (
            TypeError,
            ValueError
        ):
            pass

    # --------------------------------------------------------
    # Profile URL
    # --------------------------------------------------------

    add_evidence(
        evidence,
        "profile_url",
        profile_url,
        "Public profile reference.",
        profile
    )

    return evidence