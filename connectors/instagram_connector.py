"""
Instagram connector.

Uses an official/provider-based integration only.

No Instagram page scraping is performed.
"""

import os


def get_instagram_config():
    return {
        "access_token": os.getenv(
            "INSTAGRAM_ACCESS_TOKEN",
            ""
        ).strip(),
        "app_id": os.getenv(
            "INSTAGRAM_APP_ID",
            ""
        ).strip()
    }


def is_configured():
    config = get_instagram_config()

    return bool(
        config["access_token"]
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


def search_instagram(
    name=None,
    username=None,
    organization=None
):
    """
    Search Instagram through an authorized
    provider when configured.

    No scraping is performed.
    """

    if not is_configured():
        return []

    # Official API integration point.
    #
    # Instagram API access depends on account type,
    # permissions and application configuration.
    #
    # Implement official API calls here when
    # appropriate credentials are available.

    return []


def normalize_instagram_profile(profile):
    if not isinstance(profile, dict):
        return None

    username = normalize_username(
        profile.get("username")
        or profile.get("handle")
    )

    result = {
        "source": "instagram",
        "platform": "instagram",
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