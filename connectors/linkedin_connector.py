"""
LinkedIn connector.

This connector is intentionally provider-independent.

LinkedIn API access is restricted and normally requires
OAuth authorization and appropriate LinkedIn permissions.

This module does NOT scrape LinkedIn.
"""

import os


def get_linkedin_config():
    return {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", "").strip(),
        "client_secret": os.getenv(
            "LINKEDIN_CLIENT_SECRET",
            ""
        ).strip(),
        "access_token": os.getenv(
            "LINKEDIN_ACCESS_TOKEN",
            ""
        ).strip()
    }


def is_configured():
    config = get_linkedin_config()

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


def search_linkedin(
    name=None,
    username=None,
    organization=None
):
    """
    Search LinkedIn when an authorized provider
    is configured.

    Currently returns an empty result when no
    authorized LinkedIn provider is configured.

    No scraping is performed.
    """

    if not is_configured():
        return []

    # API integration point.
    #
    # LinkedIn access requires an approved/authorized
    # API flow. Do not scrape linkedin.com pages here.
    #
    # When credentials and permissions are available,
    # implement the official API request here.

    return []


def normalize_linkedin_profile(profile):
    if not isinstance(profile, dict):
        return None

    username = normalize_username(
        profile.get("username")
        or profile.get("handle")
    )

    result = {
        "source": "linkedin",
        "platform": "linkedin",
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
            or "headline"
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