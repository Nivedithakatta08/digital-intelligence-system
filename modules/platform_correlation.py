"""
Cross-platform identity correlation.

Important:
- Search links are NOT identity matches.
- A platform enters the knowledge graph only when an
  actual candidate/profile result has a supplied confidence
  score meeting the configured threshold.
- No platform confidence is invented here.
"""

import re


PLATFORM_CONFIDENCE_THRESHOLD = 0.75


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_username(value):
    text = normalize_text(value)

    text = text.lower()

    text = text.lstrip("@")

    return text


def normalize_score(value):
    try:
        score = float(value)
    except (
        TypeError,
        ValueError
    ):
        return 0.0

    if score > 1:
        score /= 100.0

    return max(
        0.0,
        min(
            score,
            1.0
        )
    )


def normalize_platform(value):
    text = normalize_text(value)

    if not text:
        return "Unknown"

    mapping = {
        "linkedin": "LinkedIn",
        "instagram": "Instagram",
        "instagram.com": "Instagram",
        "x": "X",
        "twitter": "X",
        "twitter.com": "X",
        "github": "GitHub",
    }

    return mapping.get(
        text.lower(),
        text
    )


def normalize_status(value):
    return normalize_text(
        value
    ).lower()


def is_actual_profile_candidate(match):
    """
    Search links are not actual identity candidates.

    We only accept records that contain an actual
    public profile URL, username, or candidate identity.
    """

    if not isinstance(
        match,
        dict
    ):
        return False

    profile_url = normalize_text(
        match.get(
            "profile_url"
        )
    )

    username = normalize_text(
        match.get(
            "username"
        )
    )

    candidate_id = normalize_text(
        match.get(
            "candidate_id"
        )
    )

    return bool(
        profile_url
        or username
        or candidate_id
    )


def username_similarity(
    left,
    right
):

    left = normalize_username(
        left
    )

    right = normalize_username(
        right
    )

    if not left or not right:
        return 0.0

    if left == right:
        return 1.0

    return 0.0


def text_similarity(
    left,
    right
):

    left = normalize_text(
        left
    ).lower()

    right = normalize_text(
        right
    ).lower()

    if not left or not right:
        return 0.0

    if left == right:
        return 1.0

    left_words = set(
        re.findall(
            r"[a-z0-9]+",
            left
        )
    )

    right_words = set(
        re.findall(
            r"[a-z0-9]+",
            right
        )
    )

    if not left_words or not right_words:
        return 0.0

    intersection = (
        left_words & right_words
    )

    union = (
        left_words | right_words
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


def get_profile_name(profile):

    return (
        profile.get("resolved_name")
        or profile.get("name")
        or profile.get("full_name")
        or profile.get("display_name")
        or ""
    )


def get_profile_username(profile):

    return (
        profile.get(
            "username"
        )
        or ""
    )


def get_profile_organization(profile):

    organization = (
        profile.get(
            "organization"
        )
        or profile.get(
            "company"
        )
        or ""
    )

    if isinstance(
        organization,
        list
    ):

        return (
            organization[0]
            if organization
            else ""
        )

    return organization


def get_profile_location(profile):

    location = profile.get(
        "location"
    )

    if isinstance(
        location,
        list
    ):

        return (
            location[0]
            if location
            else ""
        )

    return location or ""


def calculate_correlation(
    source_profile,
    platform_candidate
):

    """
    Calculate correlation from actual candidate data.

    This function does not create a match from a search URL.

    Scores are evidence measurements:
      username = exact username agreement
      name = textual name agreement
      organization = organization agreement
      location = location agreement

    Organization and location alone cannot establish identity.
    """

    if not isinstance(
        source_profile,
        dict
    ):

        return 0.0, {}

    if not isinstance(
        platform_candidate,
        dict
    ):

        return 0.0, {}


    source_username = get_profile_username(
        source_profile
    )

    candidate_username = platform_candidate.get(
        "username"
    )

    source_name = get_profile_name(
        source_profile
    )

    candidate_name = (
        platform_candidate.get(
            "name"
        )
        or platform_candidate.get(
            "full_name"
        )
        or platform_candidate.get(
            "display_name"
        )
        or ""
    )

    source_organization = (
        get_profile_organization(
            source_profile
        )
    )

    candidate_organization = (
        platform_candidate.get(
            "organization"
        )
        or platform_candidate.get(
            "company"
        )
        or ""
    )

    source_location = (
        get_profile_location(
            source_profile
        )
    )

    candidate_location = (
        platform_candidate.get(
            "location"
        )
        or ""
    )


    username_score = username_similarity(
        source_username,
        candidate_username
    )

    name_score = text_similarity(
        source_name,
        candidate_name
    )

    organization_score = text_similarity(
        source_organization,
        candidate_organization
    )

    location_score = text_similarity(
        source_location,
        candidate_location
    )


    # --------------------------------------------------------
    # Actual supplied evidence score
    # --------------------------------------------------------

    supplied_score = platform_candidate.get(
        "confidence"
    )

    if supplied_score is not None:

        confidence = normalize_score(
            supplied_score
        )

    else:

        # No external confidence was supplied.
        # Calculate from observable matching fields.

        confidence = (
            username_score * 0.50
            + name_score * 0.30
            + organization_score * 0.15
            + location_score * 0.05
        )


    # Organization alone must never become a strong match.

    if (
        username_score == 0
        and name_score == 0
    ):

        confidence = min(
            confidence,
            0.49
        )


    evidence = {

        "username_match":
            round(
                username_score,
                4
            ),

        "name_match":
            round(
                name_score,
                4
            ),

        "organization_match":
            round(
                organization_score,
                4
            ),

        "location_match":
            round(
                location_score,
                4
            )
    }


    return (
        round(
            confidence,
            4
        ),
        evidence
    )


def correlate_platform_candidate(
    source_profile,
    platform_candidate
):

    if not isinstance(
        platform_candidate,
        dict
    ):

        return None


    platform = normalize_platform(
        platform_candidate.get(
            "platform"
        )
    )


    if not is_actual_profile_candidate(
        platform_candidate
    ):

        return None


    confidence, evidence = (
        calculate_correlation(
            source_profile,
            platform_candidate
        )
    )


    result = dict(
        platform_candidate
    )


    result["platform"] = platform

    result["confidence"] = confidence

    result["correlation_score"] = confidence

    result["correlation_evidence"] = evidence


    status = normalize_status(
        platform_candidate.get(
            "status"
        )
    )


    if status == "verified_source":

        result["status"] = (
            "verified_source"
        )

    elif confidence >= PLATFORM_CONFIDENCE_THRESHOLD:

        result["status"] = (
            "high_confidence_match"
        )

    elif confidence >= 0.60:

        result["status"] = (
            "potential_match"
        )

    else:

        result["status"] = (
            "insufficient_evidence"
        )


    return result


def correlate_platform_candidates(
    source_profile,
    platform_candidates
):

    if not isinstance(
        platform_candidates,
        list
    ):

        return []


    results = []


    for candidate in platform_candidates:

        result = correlate_platform_candidate(
            source_profile,
            candidate
        )

        if result:

            results.append(
                result
            )


    return results


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def correlate_platforms(
    source_profile,
    platform_candidates
):

    return correlate_platform_candidates(
        source_profile,
        platform_candidates
    )


def correlate_profile_with_platform(
    source_profile,
    platform_candidate
):

    return correlate_platform_candidate(
        source_profile,
        platform_candidate
    )


def get_high_confidence_platforms(
    platform_matches,
    threshold=PLATFORM_CONFIDENCE_THRESHOLD
):

    results = []


    for match in platform_matches or []:

        if not isinstance(
            match,
            dict
        ):

            continue


        confidence = normalize_score(
            match.get(
                "confidence",
                0
            )
        )


        status = normalize_status(
            match.get(
                "status"
            )
        )


        if (
            confidence >= threshold
            and status in {
                "verified_source",
                "high_confidence_match"
            }
        ):

            results.append(
                match
            )


    return results