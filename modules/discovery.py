import os
import json

from connectors.github_connector import search_github_by_name
from connectors.orcid_connector import search_orcid

try:
    from connectors.crossref_connector import search_crossref
except ImportError:
    search_crossref = None

try:
    from connectors.image_identity_connector import (
        discover_identity_from_image,
        normalize_image_candidates,
    )
except ImportError:
    discover_identity_from_image = None
    normalize_image_candidates = None

try:
    from modules.platform_discovery import (
        discover_platforms_for_profile,
    )
except ImportError:
    discover_platforms_for_profile = None


# =========================================================
# CONFIGURATION
# =========================================================

# Keep this TRUE for fast demo/testing.
FAST_MODE = True

# Crossref is limited because it is an external network call.
MAX_CROSSREF_NAMES = 2


# =========================================================
# TEXT HELPERS
# =========================================================

def normalize_text(value):
    if value is None:
        return ""

    return " ".join(
        str(value).strip().lower().split()
    )


def get_profile_name(profile):
    if not isinstance(profile, dict):
        return ""

    return (
        profile.get("name")
        or profile.get("full_name")
        or profile.get("display_name")
        or ""
    )


def get_profile_username(profile):
    if not isinstance(profile, dict):
        return ""

    return (
        profile.get("username")
        or profile.get("login")
        or ""
    )


# =========================================================
# PROFILE IDENTITY KEY
# =========================================================

def profile_identity_key(profile):
    if not isinstance(profile, dict):
        return None

    candidate_id = profile.get("candidate_id")

    if candidate_id:
        return (
            "candidate",
            str(candidate_id).strip().lower()
        )

    username = normalize_text(
        get_profile_username(profile)
    )

    if username:
        return (
            "username",
            username
        )

    name = normalize_text(
        get_profile_name(profile)
    )

    if name:
        return (
            "name",
            name
        )

    return None


# =========================================================
# PROFILE DEDUPLICATION
# =========================================================

def deduplicate_profiles(profiles):
    unique = []
    seen = set()

    for profile in profiles or []:

        if not isinstance(profile, dict):
            continue

        key = profile_identity_key(
            profile
        )

        if key is None:
            continue

        if key in seen:
            continue

        seen.add(key)
        unique.append(profile)

    return unique


# =========================================================
# NORMALIZE CONNECTOR RESULTS
# =========================================================

def normalize_results(result):
    if result is None:
        return []

    if isinstance(result, dict):

        profiles = result.get(
            "profiles"
        )

        if isinstance(
            profiles,
            list
        ):
            return profiles

        return [result]

    if isinstance(result, list):

        return [
            item
            for item in result
            if isinstance(item, dict)
        ]

    return []


# =========================================================
# GITHUB DISCOVERY
# =========================================================

def discover_github(username=None):

    if not username:
        return []

    try:

        result = search_github_by_name(
            username
        )

        return normalize_results(
            result
        )

    except Exception:
        return []


# =========================================================
# ORCID DISCOVERY
# =========================================================

def discover_orcid(name):

    if not name:
        return []

    try:

        result = search_orcid(
            name
        )

        return normalize_results(
            result
        )

    except Exception:
        return []


# =========================================================
# CROSSREF DISCOVERY
# =========================================================

def discover_crossref(name):

    if not name:
        return []

    if search_crossref is None:
        return []

    try:

        result = search_crossref(
            name
        )

        if isinstance(
            result,
            dict
        ):

            publications = result.get(
                "publications",
                []
            )

            if isinstance(
                publications,
                list
            ):
                return publications

        if isinstance(
            result,
            list
        ):
            return result

    except Exception:
        pass

    return []


# =========================================================
# MOCK PROFILE LOADER
# =========================================================

def load_mock_profiles():

    mock_file = os.path.join(
        "data",
        "mock_profiles.json"
    )

    if not os.path.exists(
        mock_file
    ):
        return []

    try:

        with open(
            mock_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        if isinstance(
            data,
            list
        ):
            return data

        if isinstance(
            data,
            dict
        ):

            profiles = data.get(
                "profiles",
                []
            )

            if isinstance(
                profiles,
                list
            ):
                return profiles

    except Exception:
        pass

    return []


# =========================================================
# MOCK DISCOVERY
# =========================================================

def discover_mock(username=None):

    if not username:
        return []

    target = normalize_text(
        username
    ).lstrip("@")

    if not target:
        return []

    profiles = load_mock_profiles()

    matches = []

    for profile in profiles:

        if not isinstance(
            profile,
            dict
        ):
            continue

        profile_username = normalize_text(
            get_profile_username(profile)
        ).lstrip("@")

        if target == profile_username:

            matches.append(
                profile
            )

            continue

        aliases = profile.get(
            "aliases",
            []
        )

        if not isinstance(
            aliases,
            list
        ):
            aliases = [aliases]

        for alias in aliases:

            alias_value = normalize_text(
                alias
            ).lstrip("@")

            if target == alias_value:

                matches.append(
                    profile
                )

                break

    return matches


# =========================================================
# IMAGE DISCOVERY
# =========================================================

def discover_from_image(image):

    if image is None:

        return {
            "success": False,
            "candidates": [],
            "metadata": {},
            "error": "No image was provided."
        }

    if discover_identity_from_image is None:

        return {
            "success": False,
            "candidates": [],
            "metadata": {},
            "error": (
                "No image-to-identity provider "
                "is connected."
            )
        }

    try:

        return discover_identity_from_image(
            image
        )

    except Exception as error:

        return {
            "success": False,
            "candidates": [],
            "metadata": {},
            "error": str(error)
        }


def discover_from_image_result(result):

    if not isinstance(
        result,
        dict
    ):
        return []

    candidates = result.get(
        "candidates",
        []
    )

    if normalize_image_candidates:

        try:

            return normalize_image_candidates(
                candidates
            )

        except Exception:
            pass

    return normalize_results(
        candidates
    )


# =========================================================
# PUBLICATION DEDUPLICATION
# =========================================================

def deduplicate_publications(
    publications
):

    unique = []
    seen = set()

    for publication in publications or []:

        if not isinstance(
            publication,
            dict
        ):
            continue

        title = normalize_text(
            publication.get(
                "title"
            )
        )

        doi = normalize_text(
            publication.get(
                "doi"
            )
        )

        url = normalize_text(
            publication.get(
                "url"
            )
        )

        key = (
            doi
            or url
            or title
        )

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)

        unique.append(
            publication
        )

    return unique


# =========================================================
# ORGANIZATION ENRICHMENT
# =========================================================

def apply_organization_filter(
    profiles,
    organization
):

    if not organization:
        return profiles

    target = normalize_text(
        organization
    )

    for profile in profiles:

        if not isinstance(
            profile,
            dict
        ):
            continue

        profile_org = normalize_text(
            profile.get(
                "organization",
                ""
            )
        )

        profile[
            "organization_input_match"
        ] = bool(
            profile_org
            and profile_org == target
        )

    return profiles


# =========================================================
# PLATFORM DISCOVERY
# =========================================================

def build_platform_discovery(
    profile
):

    if (
        discover_platforms_for_profile
        is None
    ):
        return []

    if not isinstance(
        profile,
        dict
    ):
        return []

    try:

        return discover_platforms_for_profile(
            profile
        )

    except Exception:
        return []


# =========================================================
# SEARCHED NAMES
# =========================================================

def collect_searched_names(
    profiles
):

    names = []
    seen = set()

    for profile in profiles or []:

        name = get_profile_name(
            profile
        )

        normalized = normalize_text(
            name
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        names.append(name)

    return names


# =========================================================
# EXTENDED DISCOVERY
# =========================================================

def run_extended_sources(
    profiles
):

    publications = []

    if not profiles:
        return profiles, publications

    names = collect_searched_names(
        profiles
    )

    # -----------------------------------------------------
    # ORCID
    # -----------------------------------------------------

    for name in names:

        orcid_profiles = discover_orcid(
            name
        )

        profiles.extend(
            orcid_profiles
        )

    profiles = deduplicate_profiles(
        profiles
    )

    # -----------------------------------------------------
    # CROSSREF
    # -----------------------------------------------------

    for name in names[
        :MAX_CROSSREF_NAMES
    ]:

        publications.extend(
            discover_crossref(
                name
            )
        )

    publications = deduplicate_publications(
        publications
    )

    return profiles, publications


# =========================================================
# MAIN DISCOVERY
# =========================================================

def discover(
    username=None,
    organization=None,
    use_extended_sources=False
):

    profiles = []
    publications = []

    username = (
        str(username).strip()
        if username
        else ""
    )

    organization = (
        str(organization).strip()
        if organization
        else ""
    )

    # -----------------------------------------------------
    # 1. GITHUB
    # -----------------------------------------------------

    if username:

        profiles.extend(
            discover_github(
                username
            )
        )

    # -----------------------------------------------------
    # 2. MOCK DATA
    # -----------------------------------------------------

    if username:

        profiles.extend(
            discover_mock(
                username
            )
        )

    # -----------------------------------------------------
    # 3. EXTENDED SOURCES
    # -----------------------------------------------------

    if (
        use_extended_sources
        and not FAST_MODE
    ):

        profiles, publications = (
            run_extended_sources(
                profiles
            )
        )

    # -----------------------------------------------------
    # 4. DEDUPLICATE
    # -----------------------------------------------------

    profiles = deduplicate_profiles(
        profiles
    )

    publications = deduplicate_publications(
        publications
    )

    # -----------------------------------------------------
    # 5. ORGANIZATION ENRICHMENT
    # -----------------------------------------------------

    profiles = apply_organization_filter(
        profiles,
        organization
    )

    # -----------------------------------------------------
    # 6. PLATFORM SEARCH LINKS
    # -----------------------------------------------------

    platforms = []

    if profiles:

        platforms = build_platform_discovery(
            profiles[0]
        )

    # -----------------------------------------------------
    # 7. SEARCHED NAMES
    # -----------------------------------------------------

    searched_names = (
        collect_searched_names(
            profiles
        )
    )

    return {
        "profiles": profiles,
        "publications": publications,
        "image_candidates": [],
        "searched_names": searched_names,
        "platforms": platforms,
        "inputs": {
            "username": bool(username),
            "organization": bool(organization),
            "image": False
        },
        "mode": (
            "fast"
            if FAST_MODE
            else "extended"
        )
    }


# =========================================================
# COMBINED INPUT DISCOVERY
# =========================================================

def discover_from_inputs(
    username=None,
    organization=None,
    image=None,
    include_mock=True,
    use_extended_sources=False
):

    profiles = []
    publications = []
    image_candidates = []

    username = (
        str(username).strip()
        if username
        else ""
    )

    organization = (
        str(organization).strip()
        if organization
        else ""
    )

    # -----------------------------------------------------
    # 1. USERNAME → GITHUB
    # -----------------------------------------------------

    if username:

        profiles.extend(
            discover_github(
                username
            )
        )

    # -----------------------------------------------------
    # 2. MOCK DATA
    # -----------------------------------------------------

    if (
        include_mock
        and username
    ):

        profiles.extend(
            discover_mock(
                username
            )
        )

    # -----------------------------------------------------
    # 3. IMAGE
    # -----------------------------------------------------

    if image is not None:

        image_result = discover_from_image(
            image
        )

        image_candidates = (
            discover_from_image_result(
                image_result
            )
        )

        profiles.extend(
            image_candidates
        )

    # -----------------------------------------------------
    # 4. DEDUPLICATE
    # -----------------------------------------------------

    profiles = deduplicate_profiles(
        profiles
    )

    # -----------------------------------------------------
    # 5. EXTENDED SOURCES
    # -----------------------------------------------------

    if (
        use_extended_sources
        and not FAST_MODE
        and profiles
    ):

        profiles, publications = (
            run_extended_sources(
                profiles
            )
        )

    # -----------------------------------------------------
    # 6. DEDUPLICATE AGAIN
    # -----------------------------------------------------

    profiles = deduplicate_profiles(
        profiles
    )

    publications = deduplicate_publications(
        publications
    )

    # -----------------------------------------------------
    # 7. ORGANIZATION ENRICHMENT
    # -----------------------------------------------------

    profiles = apply_organization_filter(
        profiles,
        organization
    )

    # -----------------------------------------------------
    # 8. PLATFORM DISCOVERY
    # -----------------------------------------------------

    platforms = []

    if profiles:

        platforms = build_platform_discovery(
            profiles[0]
        )

    # -----------------------------------------------------
    # 9. SEARCHED NAMES
    # -----------------------------------------------------

    searched_names = (
        collect_searched_names(
            profiles
        )
    )

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {
        "profiles": profiles,
        "publications": publications,
        "image_candidates": image_candidates,
        "searched_names": searched_names,
        "platforms": platforms,
        "inputs": {
            "username": bool(username),
            "organization": bool(organization),
            "image": image is not None
        },
        "mode": (
            "fast"
            if FAST_MODE
            else "extended"
        )
    }