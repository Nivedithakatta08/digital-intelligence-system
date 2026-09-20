# =========================================================
# IDENTITY RESOLVER
# =========================================================
#
# Combines records that have strong identity evidence.
#
# Important:
# - Username is a strong identifier.
# - Candidate ID is a strong identifier.
# - Name alone is NOT enough.
# - Organization alone is NOT enough.
# - Image candidates are supporting evidence.
# =========================================================


# =========================================================
# CONFIGURATION
# =========================================================

MIN_GROUP_SCORE = 0.75


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(value):

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def normalize_username(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .lstrip("@")
    )


# =========================================================
# PROFILE GETTERS
# =========================================================

def get_name(profile):

    if not isinstance(
        profile,
        dict
    ):
        return ""

    return normalize_text(
        profile.get(
            "name"
        )
        or profile.get(
            "full_name"
        )
        or profile.get(
            "display_name"
        )
        or profile.get(
            "resolved_name"
        )
    )


def get_username(profile):

    if not isinstance(
        profile,
        dict
    ):
        return ""

    return normalize_username(
        profile.get(
            "username"
        )
        or profile.get(
            "login"
        )
    )


def get_usernames(profile):

    if not isinstance(
        profile,
        dict
    ):
        return []

    values = []

    username = get_username(
        profile
    )

    if username:
        values.append(
            username
        )

    additional = profile.get(
        "usernames",
        []
    )

    if not isinstance(
        additional,
        list
    ):
        additional = [
            additional
        ]

    for value in additional:

        username = normalize_username(
            value
        )

        if username:
            values.append(
                username
            )

    aliases = profile.get(
        "aliases",
        []
    )

    if not isinstance(
        aliases,
        list
    ):
        aliases = [
            aliases
        ]

    for value in aliases:

        username = normalize_username(
            value
        )

        if username:
            values.append(
                username
            )

    return unique_values(
        values
    )


def get_organization(profile):

    if not isinstance(
        profile,
        dict
    ):
        return ""

    organization = (
        profile.get(
            "organization"
        )
        or profile.get(
            "company"
        )
    )

    if isinstance(
        organization,
        list
    ):

        values = []

        for value in organization:

            normalized = normalize_text(
                value
            )

            if normalized:
                values.append(
                    normalized
                )

        return " ".join(
            values
        )

    return normalize_text(
        organization
    )


def get_location(profile):

    if not isinstance(
        profile,
        dict
    ):
        return ""

    location = profile.get(
        "location"
    )

    if isinstance(
        location,
        list
    ):

        values = []

        for value in location:

            normalized = normalize_text(
                value
            )

            if normalized:
                values.append(
                    normalized
                )

        return " ".join(
            values
        )

    return normalize_text(
        location
    )


# =========================================================
# GENERAL HELPERS
# =========================================================

def unique_values(values):

    result = []
    seen = set()

    for value in values or []:

        normalized = normalize_text(
            value
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        result.append(
            value
        )

    return result


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
# PROFILE IDENTITY KEY
# =========================================================

def profile_key(profile):

    if not isinstance(
        profile,
        dict
    ):
        return None

    candidate_id = normalize_text(
        profile.get(
            "candidate_id"
        )
    )

    if candidate_id:

        return (
            "candidate",
            candidate_id
        )

    username = get_username(
        profile
    )

    if username:

        return (
            "username",
            username
        )

    # Do NOT use name alone as a grouping key.
    #
    # Two people can have the same name.
    #
    name = get_name(
        profile
    )

    organization = get_organization(
        profile
    )

    if name and organization:

        return (
            "name_org",
            name,
            organization
        )

    return None


# =========================================================
# PROFILE SIMILARITY
# =========================================================

def calculate_profile_similarity(
    profile_a,
    profile_b
):

    if not isinstance(
        profile_a,
        dict
    ):
        return 0.0

    if not isinstance(
        profile_b,
        dict
    ):
        return 0.0

    score = 0.0

    # -----------------------------------------------------
    # Candidate ID
    # -----------------------------------------------------

    candidate_a = normalize_text(
        profile_a.get(
            "candidate_id"
        )
    )

    candidate_b = normalize_text(
        profile_b.get(
            "candidate_id"
        )
    )

    if (
        candidate_a
        and candidate_b
        and candidate_a == candidate_b
    ):

        return 1.0

    # -----------------------------------------------------
    # Username
    # -----------------------------------------------------

    usernames_a = set(
        get_usernames(
            profile_a
        )
    )

    usernames_b = set(
        get_usernames(
            profile_b
        )
    )

    username_match = bool(
        usernames_a
        and usernames_b
        and usernames_a.intersection(
            usernames_b
        )
    )

    # Exact username match is very strong.
    if username_match:

        score += 0.60

    # -----------------------------------------------------
    # Name
    # -----------------------------------------------------

    name_a = get_name(
        profile_a
    )

    name_b = get_name(
        profile_b
    )

    name_match = bool(
        name_a
        and name_b
        and name_a == name_b
    )

    if name_match:

        score += 0.20

    # -----------------------------------------------------
    # Organization
    # -----------------------------------------------------

    organization_a = get_organization(
        profile_a
    )

    organization_b = get_organization(
        profile_b
    )

    organization_match = bool(
        organization_a
        and organization_b
        and organization_a
        == organization_b
    )

    if organization_match:

        score += 0.10

    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------

    location_a = get_location(
        profile_a
    )

    location_b = get_location(
        profile_b
    )

    location_match = bool(
        location_a
        and location_b
        and location_a
        == location_b
    )

    if location_match:

        score += 0.10

    return round(
        min(
            score,
            1.0
        ),
        4
    )


# =========================================================
# GROUP PROFILES
# =========================================================

def group_profiles(
    profiles
):

    groups = {}

    for profile in profiles or []:

        if not isinstance(
            profile,
            dict
        ):
            continue

        key = profile_key(
            profile
        )

        if key is None:
            continue

        if key not in groups:

            groups[key] = []

        groups[key].append(
            profile
        )

    return groups


# =========================================================
# MERGE VALUES
# =========================================================

def merge_values(
    existing,
    new_value
):

    if existing in (
        None,
        "",
        []
    ):

        return new_value

    if new_value in (
        None,
        "",
        []
    ):

        return existing

    existing_values = (
        existing
        if isinstance(
            existing,
            list
        )
        else [
            existing
        ]
    )

    new_values = (
        new_value
        if isinstance(
            new_value,
            list
        )
        else [
            new_value
        ]
    )

    combined = []
    seen = set()

    for value in (
        existing_values
        + new_values
    ):

        if value is None:
            continue

        normalized = normalize_text(
            value
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        combined.append(
            value
        )

    if len(combined) == 1:

        return combined[0]

    return combined


# =========================================================
# MERGE PROFILES
# =========================================================

def merge_profiles(
    profiles
):

    if not profiles:
        return {}

    merged = {}

    for profile in profiles:

        if not isinstance(
            profile,
            dict
        ):
            continue

        for key, value in profile.items():

            if value is None:
                continue

            if key not in merged:

                merged[key] = value

            else:

                merged[key] = merge_values(
                    merged[key],
                    value
                )

    return merged


# =========================================================
# COLLECT SOURCES
# =========================================================

def collect_sources(
    profiles
):

    sources = []

    for profile in profiles or []:

        if not isinstance(
            profile,
            dict
        ):
            continue

        source = profile.get(
            "source"
        )

        if source:

            sources.append(
                source
            )

        profile_sources = profile.get(
            "sources",
            []
        )

        for item in as_list(
            profile_sources
        ):

            if item:

                sources.append(
                    item
                )

    return unique_values(
        sources
    )


# =========================================================
# IMAGE CANDIDATE MATCH
# =========================================================

def match_image_candidate(
    profile,
    image_candidates
):

    if not isinstance(
        profile,
        dict
    ):
        return None

    candidate_id = normalize_text(
        profile.get(
            "candidate_id"
        )
    )

    username = get_username(
        profile
    )

    name = get_name(
        profile
    )

    for candidate in (
        image_candidates
        or []
    ):

        if not isinstance(
            candidate,
            dict
        ):
            continue

        candidate_id_b = normalize_text(
            candidate.get(
                "candidate_id"
            )
        )

        username_b = get_username(
            candidate
        )

        name_b = get_name(
            candidate
        )

        if (
            candidate_id
            and candidate_id_b
            and candidate_id
            == candidate_id_b
        ):

            return candidate

        if (
            username
            and username_b
            and username
            == username_b
        ):

            return candidate

        if (
            name
            and name_b
            and name
            == name_b
        ):

            return candidate

    return None


# =========================================================
# BUILD RESOLVED PROFILE
# =========================================================

def build_resolved_profile(
    group,
    image_candidates=None
):

    if not group:
        return None

    merged = merge_profiles(
        group
    )

    sources = collect_sources(
        group
    )

    merged[
        "sources"
    ] = sources

    merged[
        "source_count"
    ] = len(
        sources
    )

    merged[
        "record_count"
    ] = len(
        group
    )

    # -----------------------------------------------------
    # Identity name
    # -----------------------------------------------------

    merged[
        "resolved_name"
    ] = (
        merged.get(
            "name"
        )
        or merged.get(
            "full_name"
        )
        or merged.get(
            "display_name"
        )
        or merged.get(
            "username"
        )
        or "Unknown"
    )

    # -----------------------------------------------------
    # Image candidate
    # -----------------------------------------------------

    image_match = match_image_candidate(
        merged,
        image_candidates
    )

    if image_match:

        merged[
            "image_candidate_match"
        ] = True

        similarity = (
            image_match.get(
                "image_similarity"
            )
            or image_match.get(
                "image_match_score"
            )
        )

        if similarity is not None:

            try:

                similarity = float(
                    similarity
                )

                if similarity > 1:
                    similarity /= 100

                similarity = max(
                    0.0,
                    min(
                        similarity,
                        1.0
                    )
                )

                merged[
                    "image_similarity"
                ] = round(
                    similarity,
                    4
                )

            except (
                TypeError,
                ValueError
            ):
                pass

    else:

        merged[
            "image_candidate_match"
        ] = False

    # -----------------------------------------------------
    # Record linkage
    # -----------------------------------------------------

    if len(group) <= 1:

        linkage_score = 0.50

    else:

        scores = []

        first = group[0]

        for other in group[1:]:

            scores.append(
                calculate_profile_similarity(
                    first,
                    other
                )
            )

        linkage_score = (
            sum(scores)
            / len(scores)
            if scores
            else 0.0
        )

    merged[
        "record_linkage_score"
    ] = round(
        linkage_score,
        4
    )

    # -----------------------------------------------------
    # Identity evidence
    # -----------------------------------------------------

    username_values = (
        get_usernames(
            merged
        )
    )

    merged[
        "resolved_usernames"
    ] = username_values

    merged[
        "identity_resolution"
    ] = {

        "method": "evidence_based",

        "strong_identifier": bool(
            merged.get(
                "candidate_id"
            )
            or username_values
        ),

        "record_linkage_score": round(
            linkage_score,
            4
        ),

        "source_count": len(
            sources
        )
    }

    return merged


# =========================================================
# RESOLVE
# =========================================================

def resolve(
    profiles,
    username_input=None,
    organization_input=None,
    image_candidates=None
):

    if not profiles:

        return []

    image_candidates = (
        image_candidates
        or []
    )

    groups = group_profiles(
        profiles
    )

    resolved = []

    # -----------------------------------------------------
    # Resolve strongly keyed groups
    # -----------------------------------------------------

    for group_key, group in groups.items():

        if not group:
            continue

        resolved_profile = (
            build_resolved_profile(
                group,
                image_candidates
            )
        )

        if resolved_profile:

            resolved.append(
                resolved_profile
            )

    # -----------------------------------------------------
    # Handle records that could not be strongly grouped
    #
    # Instead of throwing them away, preserve them as
    # separate unresolved candidates.
    # -----------------------------------------------------

    grouped_ids = set()

    for group in groups.values():

        for profile in group:

            grouped_ids.add(
                id(profile)
            )

    for profile in profiles:

        if not isinstance(
            profile,
            dict
        ):
            continue

        if id(profile) in grouped_ids:
            continue

        candidate = dict(
            profile
        )

        candidate[
            "resolved_name"
        ] = (
            get_name(profile)
            or get_username(profile)
            or "Unknown"
        )

        candidate[
            "sources"
        ] = collect_sources(
            [profile]
        )

        candidate[
            "source_count"
        ] = len(
            candidate[
                "sources"
            ]
        )

        candidate[
            "record_count"
        ] = 1

        candidate[
            "record_linkage_score"
        ] = 0.0

        candidate[
            "image_candidate_match"
        ] = bool(
            match_image_candidate(
                profile,
                image_candidates
            )
        )

        candidate[
            "identity_resolution"
        ] = {

            "method": "unresolved_candidate",

            "strong_identifier": False,

            "record_linkage_score": 0.0,

            "source_count": candidate[
                "source_count"
            ]
        }

        resolved.append(
            candidate
        )

    # =====================================================
    # INPUT MATCH INFORMATION
    # =====================================================

    username_target = normalize_username(
        username_input
    )

    organization_target = normalize_text(
        organization_input
    )

    for profile in resolved:

        usernames = set(
            get_usernames(
                profile
            )
        )

        profile_username = (
            username_target
            in usernames
            if username_target
            else False
        )

        profile_organization = (
            get_organization(
                profile
            )
        )

        organization_match = (
            bool(
                organization_target
                and profile_organization
                and profile_organization
                == organization_target
            )
        )

        profile[
            "input_username_match"
        ] = profile_username

        profile[
            "input_organization_match"
        ] = organization_match

    # =====================================================
    # SORT
    # =====================================================

    def sort_key(profile):

        return (

            bool(
                profile.get(
                    "input_username_match"
                )
            ),

            bool(
                profile.get(
                    "image_candidate_match"
                )
            ),

            profile.get(
                "record_linkage_score",
                0.0
            ),

            profile.get(
                "source_count",
                0
            )
        )

    resolved.sort(
        key=sort_key,
        reverse=True
    )

    return resolved


# =========================================================
# BEST RESOLVED IDENTITY
# =========================================================

def get_best_resolved_identity(
    resolved_profiles
):

    if not resolved_profiles:
        return None

    return resolved_profiles[0]


# =========================================================
# RESOLUTION SUMMARY
# =========================================================

def summarize_resolution(
    resolved_profiles
):

    if not isinstance(
        resolved_profiles,
        list
    ):
        resolved_profiles = []

    summary = {

        "total_candidates": len(
            resolved_profiles
        ),

        "username_matches": 0,

        "image_matches": 0,

        "multi_source_profiles": 0
    }

    for profile in resolved_profiles:

        if not isinstance(
            profile,
            dict
        ):
            continue

        if profile.get(
            "input_username_match"
        ):

            summary[
                "username_matches"
            ] += 1

        if profile.get(
            "image_candidate_match"
        ):

            summary[
                "image_matches"
            ] += 1

        if profile.get(
            "source_count",
            0
        ) > 1:

            summary[
                "multi_source_profiles"
            ] += 1

    return summary