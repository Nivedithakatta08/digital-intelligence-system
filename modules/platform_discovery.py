import urllib.parse


# =========================================================
# PLATFORM CONFIGURATION
# =========================================================

PLATFORMS = {

    "linkedin": {
        "name": "LinkedIn",
        "domain": "linkedin.com",
        "search_url": (
            "https://www.google.com/search?q="
            "{query}+site%3Alinkedin.com%2Fin%2F"
        )
    },

    "instagram": {
        "name": "Instagram",
        "domain": "instagram.com",
        "search_url": (
            "https://www.google.com/search?q="
            "{query}+site%3Ainstagram.com"
        )
    },

    "x": {
        "name": "X",
        "domain": "x.com",
        "search_url": (
            "https://www.google.com/search?q="
            "{query}+site%3Ax.com"
        )
    }
}


# =========================================================
# TEXT NORMALIZATION
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


def clean_username(value):

    username = normalize_username(
        value
    )

    return username.replace(
        " ",
        ""
    )


# =========================================================
# SEARCH QUERY
# =========================================================

def build_search_query(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return ""

    values = []

    username = clean_username(
        profile.get(
            "username"
        )
    )

    if username:
        values.append(
            username
        )

    name = normalize_text(
        profile.get(
            "name"
        )
        or profile.get(
            "resolved_name"
        )
        or profile.get(
            "full_name"
        )
    )

    if name:
        values.append(
            name
        )

    organization = normalize_text(
        profile.get(
            "organization"
        )
    )

    if organization:
        values.append(
            organization
        )

    # Remove duplicates
    result = []
    seen = set()

    for value in values:

        if value in seen:
            continue

        seen.add(value)

        result.append(
            value
        )

    return " ".join(
        result
    )


# =========================================================
# PLATFORM SEARCH URL
# =========================================================

def build_platform_search_url(
    platform_key,
    profile
):

    platform = PLATFORMS.get(
        platform_key
    )

    if not platform:
        return ""

    query = build_search_query(
        profile
    )

    if not query:
        return ""

    encoded_query = (
        urllib.parse.quote_plus(
            query
        )
    )

    return platform[
        "search_url"
    ].format(
        query=encoded_query
    )


# =========================================================
# CREATE SEARCH RECORD
# =========================================================

def create_platform_search(
    platform_key,
    profile
):

    platform = PLATFORMS.get(
        platform_key
    )

    if not platform:
        return None

    search_url = (
        build_platform_search_url(
            platform_key,
            profile
        )
    )

    if not search_url:
        return None

    return {

        "platform": platform_key,

        "platform_name": platform[
            "name"
        ],

        "domain": platform[
            "domain"
        ],

        "search_url": search_url,

        "status": "search_link",

        "verified": False,

        "potential_match": False,

        "profile_url": None,

        "confidence": 0.0
    }


# =========================================================
# DISCOVER PLATFORMS
# =========================================================

def discover_platforms(
    profile
):

    if not isinstance(
        profile,
        dict
    ):
        return []

    results = []

    for platform_key in PLATFORMS:

        result = create_platform_search(
            platform_key,
            profile
        )

        if result:

            results.append(
                result
            )

    return results


# =========================================================
# PROFILE-BASED DISCOVERY
# =========================================================

def discover_platforms_for_profile(
    profile
):

    return discover_platforms(
        profile
    )


# =========================================================
# ADD ACTUAL PLATFORM MATCH
# =========================================================

def create_platform_match(
    platform,
    profile_url,
    name=None,
    username=None,
    organization=None,
    bio=None,
    location=None
):

    platform_key = normalize_text(
        platform
    )

    if platform_key not in PLATFORMS:
        return None

    return {

        "platform": platform_key,

        "platform_name": PLATFORMS[
            platform_key
        ]["name"],

        "domain": PLATFORMS[
            platform_key
        ]["domain"],

        "search_url": None,

        "profile_url": profile_url,

        "status": "potential_match",

        "verified": False,

        "potential_match": True,

        "name": name,

        "username": username,

        "organization": organization,

        "bio": bio,

        "location": location,

        "confidence": 0.0
    }


# =========================================================
# MARK VERIFIED PLATFORM SOURCE
# =========================================================

def mark_platform_verified(
    platform_match,
    confidence
):

    if not isinstance(
        platform_match,
        dict
    ):
        return platform_match

    updated = dict(
        platform_match
    )

    updated[
        "status"
    ] = "verified_source"

    updated[
        "verified"
    ] = True

    updated[
        "potential_match"
    ] = False

    try:

        confidence = float(
            confidence
        )

        if confidence > 1:
            confidence /= 100

    except (
        TypeError,
        ValueError
    ):

        confidence = 0.0

    updated[
        "confidence"
    ] = max(
        0.0,
        min(
            confidence,
            1.0
        )
    )

    return updated


# =========================================================
# PLATFORM SUMMARY
# =========================================================

def summarize_platform_discovery(
    results
):

    if not isinstance(
        results,
        list
    ):
        results = []

    summary = {

        "total": len(
            results
        ),

        "search_links": 0,

        "potential_matches": 0,

        "verified_sources": 0
    }

    for result in results:

        if not isinstance(
            result,
            dict
        ):
            continue

        status = result.get(
            "status"
        )

        if status == "search_link":

            summary[
                "search_links"
            ] += 1

        elif status == "potential_match":

            summary[
                "potential_matches"
            ] += 1

        elif status == "verified_source":

            summary[
                "verified_sources"
            ] += 1

    return summary


# =========================================================
# GET PLATFORM NAMES
# =========================================================

def get_platform_names():

    return [
        platform[
            "name"
        ]
        for platform in PLATFORMS.values()
    ]