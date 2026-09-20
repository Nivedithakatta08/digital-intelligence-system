# ============================================================
# GRAPH THRESHOLD
# ============================================================

GRAPH_CONFIDENCE_THRESHOLD = 0.75


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):

    try:
        value = float(value)

    except (
        TypeError,
        ValueError
    ):

        return minimum

    return max(
        minimum,
        min(
            value,
            maximum
        )
    )


def normalize_score(value):

    try:
        value = float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0

    if value > 1.0:
        value /= 100.0

    return clamp(value)


# ============================================================
# USERNAME MATCH
# ============================================================

def calculate_username_match(
    profile,
    username_input=None
):

    if (
        not isinstance(profile, dict)
        or not username_input
    ):
        return 0.0

    target = (
        str(username_input)
        .strip()
        .lower()
        .lstrip("@")
    )

    if not target:
        return 0.0

    values = []

    username = profile.get(
        "username"
    )

    if username:
        values.append(username)

    usernames = profile.get(
        "usernames",
        []
    )

    if isinstance(
        usernames,
        list
    ):
        values.extend(
            usernames
        )

    elif usernames:
        values.append(
            usernames
        )

    aliases = profile.get(
        "aliases",
        []
    )

    if isinstance(
        aliases,
        list
    ):
        values.extend(
            aliases
        )

    elif aliases:
        values.append(
            aliases
        )

    for value in values:

        normalized = (
            str(value)
            .strip()
            .lower()
            .lstrip("@")
        )

        if normalized == target:
            return 1.0

    return 0.0


# ============================================================
# ORGANIZATION MATCH
# ============================================================

def calculate_organization_match(
    profile,
    organization_input=None
):

    if (
        not isinstance(profile, dict)
        or not organization_input
    ):
        return 0.0

    target = (
        str(organization_input)
        .strip()
        .lower()
    )

    values = []

    organization = profile.get(
        "organization"
    )

    if isinstance(
        organization,
        list
    ):
        values.extend(
            organization
        )

    elif organization:
        values.append(
            organization
        )

    organizations = profile.get(
        "organizations"
    )

    if isinstance(
        organizations,
        list
    ):
        values.extend(
            organizations
        )

    elif organizations:
        values.append(
            organizations
        )

    for value in values:

        if not value:
            continue

        if (
            str(value)
            .strip()
            .lower()
            == target
        ):
            return 1.0

    return 0.0


# ============================================================
# IMAGE SCORE
# ============================================================

def calculate_image_score(profile):

    if not isinstance(
        profile,
        dict
    ):
        return 0.0

    value = profile.get(
        "image_similarity"
    )

    if value is None:

        value = profile.get(
            "image_match_score"
        )

    if value is None:
        return 0.0

    return normalize_score(
        value
    )


# ============================================================
# SOURCE SCORE
# ============================================================

def calculate_source_score(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return 0.0

    try:

        source_count = int(
            profile.get(
                "source_count",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        source_count = 0

    if source_count <= 0:
        return 0.0

    if source_count == 1:
        return 0.40

    if source_count == 2:
        return 0.70

    return 1.0


# ============================================================
# LINKAGE SCORE
# ============================================================

def calculate_linkage_score(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return 0.0

    return normalize_score(
        profile.get(
            "record_linkage_score",
            0.0
        )
    )


# ============================================================
# EVIDENCE SCORE
# ============================================================

def calculate_evidence_score(
    profile,
    evidence=None
):

    if (
        not isinstance(profile, dict)
        or not isinstance(evidence, list)
    ):
        return 0.0

    candidate_id = profile.get(
        "candidate_id"
    )

    count = 0

    for item in evidence:

        if not isinstance(
            item,
            dict
        ):
            continue

        evidence_candidate = item.get(
            "candidate_id"
        )

        if (
            candidate_id
            and evidence_candidate
            and str(candidate_id)
            == str(evidence_candidate)
        ):

            count += 1

        elif not evidence_candidate:

            count += 1

    if count == 0:
        return 0.0

    if count == 1:
        return 0.25

    if count == 2:
        return 0.50

    return 0.75


# ============================================================
# CONFLICT PENALTY
# ============================================================

def calculate_conflict_penalty(
    conflicts=None
):

    if not isinstance(
        conflicts,
        list
    ):
        return 0.0

    penalty = 0.0

    for conflict in conflicts:

        if not isinstance(
            conflict,
            dict
        ):

            penalty += 0.05
            continue

        severity = str(
            conflict.get(
                "severity",
                ""
            )
        ).lower()

        if severity == "high":

            penalty += 0.20

        elif severity == "medium":

            penalty += 0.10

        else:

            penalty += 0.05

    return clamp(
        penalty,
        0.0,
        0.50
    )


# ============================================================
# CANDIDATE ANCHOR
# ============================================================

def calculate_candidate_anchor_score(
    profile,
    username_input=None,
    organization_input=None
):

    if not isinstance(
        profile,
        dict
    ):
        return 0.0

    username_score = calculate_username_match(
        profile,
        username_input
    )

    image_score = calculate_image_score(
        profile
    )

    organization_score = calculate_organization_match(
        profile,
        organization_input
    )

    if username_score == 1.0:
        return 1.0

    if image_score >= 0.90:
        return image_score

    if organization_score == 1.0:
        return 0.60

    return max(
        username_score,
        image_score,
        organization_score
    )


# ============================================================
# FINAL CONFIDENCE
# ============================================================

def calculate_confidence(
    profile,
    evidence=None,
    conflicts=None,
    username_input=None,
    organization_input=None
):

    username_score = calculate_username_match(
        profile,
        username_input
    )

    image_score = calculate_image_score(
        profile
    )

    source_score = calculate_source_score(
        profile
    )

    linkage_score = calculate_linkage_score(
        profile
    )

    evidence_score = calculate_evidence_score(
        profile,
        evidence
    )

    organization_score = calculate_organization_match(
        profile,
        organization_input
    )

    conflict_penalty = calculate_conflict_penalty(
        conflicts
    )

    score_value = (

        username_score * 0.35

        + image_score * 0.30

        + source_score * 0.15

        + linkage_score * 0.10

        + evidence_score * 0.05

        + organization_score * 0.05

    )

    score_value -= conflict_penalty

    return round(
        clamp(score_value),
        4
    )


# ============================================================
# CONFIDENCE LABEL
# ============================================================

def confidence_label(
    score_value
):

    score_value = normalize_score(
        score_value
    )

    if score_value >= 0.80:
        return "High confidence"

    if score_value >= 0.65:
        return "Moderate confidence"

    if score_value >= 0.50:
        return "Low confidence"

    return "Very low confidence"


# ============================================================
# SCORE PROFILE
# ============================================================

def score_profile(
    profile,
    evidence=None,
    conflicts=None,
    username_input=None,
    organization_input=None
):

    if not isinstance(
        profile,
        dict
    ):
        return None

    scored = dict(
        profile
    )

    username_score = calculate_username_match(
        profile,
        username_input
    )

    image_score = calculate_image_score(
        profile
    )

    source_score = calculate_source_score(
        profile
    )

    linkage_score = calculate_linkage_score(
        profile
    )

    evidence_score = calculate_evidence_score(
        profile,
        evidence
    )

    organization_score = calculate_organization_match(
        profile,
        organization_input
    )

    anchor_score = calculate_candidate_anchor_score(
        profile,
        username_input,
        organization_input
    )

    conflict_penalty = calculate_conflict_penalty(
        conflicts
    )

    final_score = calculate_confidence(
        profile,
        evidence=evidence,
        conflicts=conflicts,
        username_input=username_input,
        organization_input=organization_input
    )

    scored[
        "username_match_score"
    ] = round(
        username_score,
        4
    )

    scored[
        "image_score"
    ] = round(
        image_score,
        4
    )

    scored[
        "source_score"
    ] = round(
        source_score,
        4
    )

    scored[
        "record_linkage_score"
    ] = round(
        linkage_score,
        4
    )

    scored[
        "evidence_score"
    ] = round(
        evidence_score,
        4
    )

    scored[
        "organization_match_score"
    ] = round(
        organization_score,
        4
    )

    scored[
        "candidate_anchor_score"
    ] = round(
        anchor_score,
        4
    )

    scored[
        "conflict_penalty"
    ] = round(
        conflict_penalty,
        4
    )

    scored[
        "confidence"
    ] = final_score

    scored[
        "confidence_percentage"
    ] = round(
        final_score * 100,
        2
    )

    scored[
        "confidence_label"
    ] = confidence_label(
        final_score
    )

    return scored


# ============================================================
# SCORE ALL PROFILES
# ============================================================

def score(
    profiles,
    evidence=None,
    conflicts=None,
    username_input=None,
    organization_input=None
):

    if not profiles:
        return []

    scored_profiles = []

    for profile in profiles:

        result = score_profile(
            profile,
            evidence=evidence,
            conflicts=conflicts,
            username_input=username_input,
            organization_input=organization_input
        )

        if result is not None:

            scored_profiles.append(
                result
            )

    scored_profiles.sort(
        key=lambda profile: (
            profile.get(
                "confidence",
                0.0
            ),
            profile.get(
                "candidate_anchor_score",
                0.0
            ),
            profile.get(
                "source_count",
                0
            )
        ),
        reverse=True
    )

    return scored_profiles


# ============================================================
# GRAPH RELATIONSHIP FILTER
# ============================================================

def filter_high_confidence_relationships(
    relationships,
    threshold=GRAPH_CONFIDENCE_THRESHOLD
):

    if not isinstance(
        relationships,
        list
    ):
        return []

    threshold = normalize_score(
        threshold
    )

    filtered = []

    for relationship in relationships:

        if not isinstance(
            relationship,
            dict
        ):
            continue

        confidence = relationship.get(
            "relationship_confidence"
        )

        if confidence is None:

            confidence = relationship.get(
                "confidence"
            )

        if confidence is None:

            confidence = relationship.get(
                "score"
            )

        confidence = normalize_score(
            confidence
        )

        if confidence >= threshold:

            item = dict(
                relationship
            )

            item[
                "relationship_confidence"
            ] = round(
                confidence,
                4
            )

            filtered.append(
                item
            )

    return filtered


# ============================================================
# BEST CANDIDATE
# ============================================================

def get_best_candidate(
    profiles
):

    if not profiles:
        return None

    return max(
        profiles,
        key=lambda profile:
        profile.get(
            "confidence",
            0.0
        )
    )