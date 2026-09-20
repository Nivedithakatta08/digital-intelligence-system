import os
import requests


# =========================================================
# CONFIGURATION
# =========================================================

GITHUB_API = "https://api.github.com"

REQUEST_TIMEOUT = 10

MAX_SEARCH_RESULTS = 10
MAX_REPOSITORIES = 20


# =========================================================
# SESSION
# =========================================================

session = requests.Session()

session.headers.update(
    {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Digital-Identity-Intelligence-System"
    }
)


# =========================================================
# OPTIONAL GITHUB TOKEN
# =========================================================

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    ""
).strip()

if GITHUB_TOKEN:

    session.headers.update(
        {
            "Authorization": f"Bearer {GITHUB_TOKEN}"
        }
    )


# =========================================================
# HELPERS
# =========================================================

def normalize_username(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .lstrip("@")
    )


def safe_text(value):

    if value is None:
        return ""

    return str(value).strip()


def safe_request(url, params=None):

    try:

        response = session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        return response

    except requests.RequestException:

        return None


# =========================================================
# FETCH SINGLE GITHUB PROFILE
# =========================================================

def get_github_profile(username):

    username = normalize_username(
        username
    )

    if not username:
        return None

    url = (
        f"{GITHUB_API}/users/"
        f"{username}"
    )

    response = safe_request(
        url
    )

    if response is None:
        return None

    if response.status_code != 200:
        return None

    try:

        data = response.json()

    except ValueError:

        return None

    if not isinstance(
        data,
        dict
    ):
        return None

    return data


# =========================================================
# FETCH REPOSITORIES
# =========================================================

def get_github_repositories(
    username
):

    username = normalize_username(
        username
    )

    if not username:
        return []

    url = (
        f"{GITHUB_API}/users/"
        f"{username}/repos"
    )

    response = safe_request(
        url,
        params={
            "per_page": MAX_REPOSITORIES,
            "sort": "updated",
            "direction": "desc"
        }
    )

    if response is None:
        return []

    if response.status_code != 200:
        return []

    try:

        data = response.json()

    except ValueError:

        return []

    if not isinstance(
        data,
        list
    ):
        return []

    repositories = []

    for repo in data:

        if not isinstance(
            repo,
            dict
        ):
            continue

        repository = {
            "name": repo.get(
                "name"
            ),
            "description": repo.get(
                "description"
            ),
            "url": repo.get(
                "html_url"
            ),
            "language": repo.get(
                "language"
            ),
            "created_at": repo.get(
                "created_at"
            ),
            "updated_at": repo.get(
                "updated_at"
            ),
            "stars": repo.get(
                "stargazers_count",
                0
            ),
            "forks": repo.get(
                "forks_count",
                0
            )
        }

        repositories.append(
            repository
        )

    return repositories


# =========================================================
# NORMALIZE GITHUB PROFILE
# =========================================================

def normalize_github_profile(
    profile,
    include_repositories=True
):

    if not isinstance(
        profile,
        dict
    ):
        return None

    login = safe_text(
        profile.get(
            "login"
        )
    )

    if not login:
        return None

    name = safe_text(
        profile.get(
            "name"
        )
    )

    bio = safe_text(
        profile.get(
            "bio"
        )
    )

    company = safe_text(
        profile.get(
            "company"
        )
    )

    location = safe_text(
        profile.get(
            "location"
        )
    )

    profile_url = safe_text(
        profile.get(
            "html_url"
        )
    )

    avatar_url = safe_text(
        profile.get(
            "avatar_url"
        )
    )

    created_at = safe_text(
        profile.get(
            "created_at"
        )
    )

    updated_at = safe_text(
        profile.get(
            "updated_at"
        )
    )

    public_repositories = (
        profile.get(
            "public_repos",
            0
        )
    )

    followers = (
        profile.get(
            "followers",
            0
        )
    )

    following = (
        profile.get(
            "following",
            0
        )
    )

    normalized = {

        "source": "github",

        "candidate_id": (
            f"github:{login.lower()}"
        ),

        "name": (
            name
            or login
        ),

        "username": login,

        "organization": (
            company
            or None
        ),

        "bio": (
            bio
            or None
        ),

        "location": (
            location
            or None
        ),

        "profile_url": (
            profile_url
            or None
        ),

        "avatar_url": (
            avatar_url
            or None
        ),

        "github_created_at": (
            created_at
            or None
        ),

        "github_updated_at": (
            updated_at
            or None
        ),

        "public_repositories": (
            public_repositories
        ),

        "followers": followers,

        "following": following
    }


    # -----------------------------------------------------
    # REPOSITORIES
    # -----------------------------------------------------

    if include_repositories:

        repositories = (
            get_github_repositories(
                login
            )
        )

        normalized[
            "projects"
        ] = repositories

    else:

        normalized[
            "projects"
        ] = []


    return normalized


# =========================================================
# EXACT USERNAME LOOKUP
# =========================================================

def get_github_user(
    username
):

    profile = get_github_profile(
        username
    )

    if profile is None:
        return None

    return normalize_github_profile(
        profile
    )


# =========================================================
# SEARCH GITHUB USERS
# =========================================================

def search_github_users(
    query
):

    query = safe_text(
        query
    )

    if not query:
        return []

    url = (
        f"{GITHUB_API}/search/users"
    )

    response = safe_request(
        url,
        params={
            "q": query,
            "per_page": MAX_SEARCH_RESULTS
        }
    )

    if response is None:
        return []

    if response.status_code != 200:
        return []

    try:

        data = response.json()

    except ValueError:

        return []

    if not isinstance(
        data,
        dict
    ):
        return []

    return data.get(
        "items",
        []
    )


# =========================================================
# SEARCH BY USERNAME
# =========================================================

def search_github_by_name(
    name
):

    """
    Discover GitHub profiles using a username.

    Exact username lookup is attempted first.

    Fuzzy search is used only as a fallback and
    results are marked as candidate matches rather
    than automatically treated as confirmed.
    """

    target = normalize_username(
        name
    )

    if not target:
        return []


    # =====================================================
    # 1. EXACT PROFILE LOOKUP
    # =====================================================

    exact_profile = get_github_user(
        target
    )

    if exact_profile:

        exact_profile[
            "match_type"
        ] = "exact_username"

        exact_profile[
            "username_match"
        ] = True

        exact_profile[
            "discovery_confidence"
        ] = 1.0

        return [
            exact_profile
        ]


    # =====================================================
    # 2. FALLBACK SEARCH
    # =====================================================

    search_results = (
        search_github_users(
            target
        )
    )

    profiles = []

    for user in search_results:

        if not isinstance(
            user,
            dict
        ):
            continue

        login = safe_text(
            user.get(
                "login"
            )
        )

        if not login:
            continue

        normalized_login = (
            normalize_username(
                login
            )
        )

        # -------------------------------------------------
        # Exact result from search
        # -------------------------------------------------

        if normalized_login == target:

            profile = get_github_user(
                login
            )

            if profile:

                profile[
                    "match_type"
                ] = "exact_username"

                profile[
                    "username_match"
                ] = True

                profile[
                    "discovery_confidence"
                ] = 1.0

                profiles.append(
                    profile
                )

                continue

        # -------------------------------------------------
        # Non-exact candidate
        # -------------------------------------------------

        candidate = {

            "source": "github",

            "candidate_id": (
                f"github:{normalized_login}"
            ),

            "name": (
                user.get(
                    "login"
                )
                or normalized_login
            ),

            "username": login,

            "organization": None,

            "bio": None,

            "location": None,

            "profile_url": (
                user.get(
                    "html_url"
                )
            ),

            "avatar_url": (
                user.get(
                    "avatar_url"
                )
            ),

            "match_type": (
                "search_candidate"
            ),

            "username_match": False,

            "discovery_confidence": 0.30
        }

        profiles.append(
            candidate
        )


    return profiles


# =========================================================
# PUBLIC CONNECTOR FUNCTION
# =========================================================

def search_github_by_username(
    username
):

    return search_github_by_name(
        username
    )