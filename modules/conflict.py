# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


def values_as_list(value):

    if value is None:
        return []

    if isinstance(
        value,
        list
    ):
        return [
            item
            for item in value
            if item
        ]

    return [value]


# ============================================================
# CONFLICT CREATION
# ============================================================

def make_conflict(
    field,
    values,
    severity="medium"
):

    cleaned = []

    for value in values:

        if value is None:
            continue

        if isinstance(
            value,
            list
        ):
            cleaned.extend(
                str(item)
                for item in value
                if item
            )

        else:
            cleaned.append(
                str(value)
            )

    unique = []

    seen = set()

    for value in cleaned:

        key = normalize(
            value
        )

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        unique.append(
            value
        )

    if len(unique) <= 1:
        return None

    field_label = field.replace(
        "_",
        " "
    ).title()

    value_text = ", ".join(
        unique
    )

    simple_description = (
        f"Different {field_label.lower()} "
        f"values were found across sources: "
        f"{value_text}."
    )

    return {
        "type": "field_conflict",
        "field": field,
        "severity": severity,
        "values": unique,
        "description": simple_description,
        "simple_description": simple_description
    }


# ============================================================
# CONFLICT DETECTION
# ============================================================

def detect_conflicts(
    profiles
):

    if not profiles:
        return []

    conflicts = []

    # --------------------------------------------------------
    # Names
    # --------------------------------------------------------

    names = []

    for profile in profiles:

        value = (
            profile.get("name")
            or profile.get("full_name")
            or profile.get("display_name")
        )

        if value:
            names.append(
                value
            )

    conflict = make_conflict(
        "name",
        names,
        severity="high"
    )

    if conflict:
        conflicts.append(
            conflict
        )

    # --------------------------------------------------------
    # Usernames
    # --------------------------------------------------------

    usernames = []

    for profile in profiles:

        username = profile.get(
            "username"
        )

        if username:
            usernames.append(
                username
            )

    conflict = make_conflict(
        "username",
        usernames,
        severity="medium"
    )

    if conflict:
        conflicts.append(
            conflict
        )

    # --------------------------------------------------------
    # Organizations
    # --------------------------------------------------------

    organizations = []

    for profile in profiles:

        value = (
            profile.get("organization")
            or profile.get("organizations")
        )

        organizations.extend(
            values_as_list(value)
        )

    conflict = make_conflict(
        "organization",
        organizations,
        severity="medium"
    )

    if conflict:
        conflicts.append(
            conflict
        )

    # --------------------------------------------------------
    # Locations
    # --------------------------------------------------------

    locations = []

    for profile in profiles:

        value = (
            profile.get("location")
            or profile.get("locations")
        )

        locations.extend(
            values_as_list(value)
        )

    conflict = make_conflict(
        "location",
        locations,
        severity="low"
    )

    if conflict:
        conflicts.append(
            conflict
        )

    # --------------------------------------------------------
    # Candidate IDs
    # --------------------------------------------------------

    candidate_ids = []

    for profile in profiles:

        value = profile.get(
            "candidate_id"
        )

        if value:
            candidate_ids.append(
                value
            )

    conflict = make_conflict(
        "candidate_id",
        candidate_ids,
        severity="high"
    )

    if conflict:
        conflicts.append(
            conflict
        )

    return conflicts