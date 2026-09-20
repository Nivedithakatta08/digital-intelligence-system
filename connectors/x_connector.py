"""
X connector.

Uses the official X API when an access token
is configured.

No X/Twitter page scraping is performed.
"""

import os


def get_x_config():
    return {
        "bearer_token": os.getenv(
            "X_BEARER_TOKEN",
            ""
        ).strip()
    }


def is_configured():
    config = get_x_config()

    return bool(
        config["bearer_token"]
    )


def normalize_username(value):
    if not value:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .lstrip("@")
    )


def search_x(
    name=None,
    username=None,
    organization=None
):
    """
    Search X through the official API when
    configured.

    The actual API request will be added once
    an X API credential is configured.
    """

    if not is_configured():
        return []

    # Official X API integration point.
    #
    # The API supports authenticated user lookup.
    # Broader discovery depends on the available
    # API access level.
    #
    # Do not scrape x.com here.

    return []


def normalize_x_profile(profile):
    if not isinstance(profile, dict):
        return None

    username = normalize_username(
        profile.get("username")
        or profile.get("handle")
    )

    result = {
        "source": "x",
        "platform": "x",
        "name": profile.get(
            "name"
            or "full_name"
            or "display_name"
        ),
        "username": username,
        "organization": profile.get(
            "organization"
        ),
        "bio": profile.get(
            "bio"
            or "description"
        ),
        "location": profile.get(
            "location"
        ),
        "profile_url": profile.get(
            "profile_url"
            or "url"
        ),
    }

    return {
        key: value
        for key, value in result.items()
        if value not in (None, "", [])
    }