from pathlib import Path
from urllib.parse import urlparse
import re


# ============================================================
# HELPERS
# ============================================================

def _text(value):
    """
    Convert arbitrary values into a safe display string.
    Prevents unhashable list/dict errors.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, dict):

        for key in (
            "name",
            "title",
            "label",
            "value",
            "display_name",
            "username",
            "login",
            "platform",
            "source",
            "url"
        ):

            if value.get(key):
                return _text(value[key])

        return ""

    if isinstance(value, (list, tuple, set)):

        values = []

        for item in value:

            text = _text(item)

            if text:
                values.append(text)

        return ", ".join(values)

    return str(value).strip()


def _items(value):
    """
    Safely convert a field into a list of usable values.
    """

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return list(value)

    return [value]


def _slug(value):
    """
    Create a safe node identifier.
    """

    value = _text(value).lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value
    )

    value = value.strip("_")

    return value[:80] or "unknown"


def _unique(values):
    """
    Preserve order while removing duplicates.
    """

    result = []
    seen = set()

    for value in values:

        value = _text(value)

        if not value:
            continue

        key = value.lower()

        if key not in seen:

            seen.add(key)
            result.append(value)

    return result


def _url_host(url):
    """
    Extract hostname from a URL.
    """

    if not isinstance(url, str):
        return ""

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return ""

    try:

        host = urlparse(url).netloc.lower()

        if host.startswith("www."):
            host = host[4:]

        return host

    except Exception:

        return ""


def _pretty_platform(host):
    """
    Convert common domains into readable platform names.
    """

    mapping = {

        "github.com": "GitHub",
        "gitlab.com": "GitLab",
        "linkedin.com": "LinkedIn",
        "twitter.com": "X / Twitter",
        "x.com": "X / Twitter",
        "facebook.com": "Facebook",
        "instagram.com": "Instagram",
        "youtube.com": "YouTube",
        "orcid.org": "ORCID",
        "scholar.google.com": "Google Scholar",
        "researchgate.net": "ResearchGate",
        "stackoverflow.com": "Stack Overflow",
        "medium.com": "Medium",
        "dev.to": "Dev.to"

    }

    return mapping.get(
        host,
        host
    )


def _add_node(graph, node_id, label, node_type):

    graph.add_node(
        node_id,
        label=label,
        node_type=node_type
    )


def _add_edge(
    graph,
    source,
    target,
    relation=""
):

    if not source or not target:
        return

    graph.add_edge(
        source,
        target,
        relation=relation
    )


# ============================================================
# PLATFORM EXTRACTION
# ============================================================

def _extract_platforms(record):
    """
    Extract platform names from a profile record.

    Uses explicit platform fields first.
    If unavailable, attempts to infer platform from URLs.
    """

    platforms = []

    if not isinstance(record, dict):
        return platforms

    explicit_keys = [
        "platform",
        "platform_name",
        "platforms",
        "site",
        "network",
        "provider"
    ]

    for key in explicit_keys:

        for item in _items(record.get(key)):

            if isinstance(item, dict):

                value = (
                    item.get("name")
                    or item.get("platform")
                    or item.get("site")
                    or item.get("source")
                )

            else:

                value = item

            value = _text(value)

            if value:
                platforms.append(value)

    # Source fields
    for key in ["source", "sources"]:

        for item in _items(record.get(key)):

            if isinstance(item, dict):

                value = (
                    item.get("platform")
                    or item.get("name")
                    or item.get("source")
                    or item.get("url")
                )

            else:

                value = item

            value = _text(value)

            if not value:
                continue

            host = _url_host(value)

            if host:

                platforms.append(
                    _pretty_platform(host)
                )

            else:

                platforms.append(value)

    # URL-based detection
    url_keys = [
        "url",
        "profile_url",
        "profile",
        "html_url",
        "link"
    ]

    for key in url_keys:

        for item in _items(record.get(key)):

            value = _text(item)

            host = _url_host(value)

            if host:

                platforms.append(
                    _pretty_platform(host)
                )

    return _unique(platforms)


# ============================================================
# PROFILE URL
# ============================================================

def _extract_url(record):

    if not isinstance(record, dict):
        return ""

    for key in (
        "profile_url",
        "url",
        "html_url",
        "link",
        "profile"
    ):

        value = record.get(key)

        if isinstance(value, str) and value.strip():

            return value.strip()

    return ""


# ============================================================
# GENERIC ENTITY EXTRACTION
# ============================================================

def _extract_values(record, keys):

    values = []

    if not isinstance(record, dict):
        return values

    for key in keys:

        if key not in record:
            continue

        for item in _items(record.get(key)):

            value = _text(item)

            if value:
                values.append(value)

    return _unique(values)


# ============================================================
# MAIN GRAPH BUILDER
# ============================================================

def build_graph(
    candidate,
    publications=None,
    profiles=None,
    discovered_profiles=None
):

    """
    Build a real identity knowledge graph.

    Parameters
    ----------
    candidate:
        Best resolved identity.

    publications:
        Discovered publications.

    profiles:
        Resolved profile records.

    discovered_profiles:
        Raw discovery records.

    Returns
    -------
    str | None
        Path to generated PNG.
    """

    # --------------------------------------------------------
    # Lazy imports
    # --------------------------------------------------------

    try:

        import matplotlib

        matplotlib.use("Agg")

        import matplotlib.pyplot as plt
        import networkx as nx

    except ImportError:

        return None

    # --------------------------------------------------------
    # Normalize inputs
    # --------------------------------------------------------

    if not isinstance(candidate, dict):
        candidate = {}

    if not isinstance(publications, list):
        publications = []

    if not isinstance(profiles, list):
        profiles = []

    if not isinstance(discovered_profiles, list):
        discovered_profiles = []

    # Candidate may itself contain profiles
    candidate_profiles = candidate.get("profiles")

    if isinstance(candidate_profiles, list):

        profiles = profiles + candidate_profiles

    # Combine resolved + discovered profiles
    all_profiles = []

    all_profiles.extend(profiles)
    all_profiles.extend(discovered_profiles)

    # --------------------------------------------------------
    # Create graph
    # --------------------------------------------------------

    graph = nx.Graph()

    # --------------------------------------------------------
    # PERSON
    # --------------------------------------------------------

    person_name = (
        candidate.get("resolved_name")
        or candidate.get("name")
        or candidate.get("display_name")
        or candidate.get("username")
        or "Unknown Person"
    )

    person_id = "person:" + _slug(person_name)

    _add_node(
        graph,
        person_id,
        person_name,
        "Person"
    )

    # --------------------------------------------------------
    # USERNAME
    # --------------------------------------------------------

    username = (
        candidate.get("username")
        or candidate.get("login")
    )

    if username:

        username_id = (
            "username:" +
            _slug(username)
        )

        _add_node(
            graph,
            username_id,
            "@" + _text(username),
            "Username"
        )

        _add_edge(
            graph,
            person_id,
            username_id,
            "uses"
        )


    # ========================================================
    # CANDIDATE ATTRIBUTES
    # ========================================================

    # --------------------------------------------------------
    # ALIASES
    # --------------------------------------------------------

    aliases = _extract_values(
        candidate,
        [
            "aliases",
            "alias",
            "other_names"
        ]
    )

    for alias in aliases:

        alias_id = (
            "alias:" +
            _slug(alias)
        )

        _add_node(
            graph,
            alias_id,
            alias,
            "Alias"
        )

        _add_edge(
            graph,
            person_id,
            alias_id,
            "also known as"
        )


    # --------------------------------------------------------
    # ORGANIZATIONS
    # --------------------------------------------------------

    organizations = _extract_values(
        candidate,
        [
            "organization",
            "organizations",
            "company",
            "companies",
            "employer"
        ]
    )

    for organization in organizations:

        org_id = (
            "organization:" +
            _slug(organization)
        )

        _add_node(
            graph,
            org_id,
            organization,
            "Organization"
        )

        _add_edge(
            graph,
            person_id,
            org_id,
            "associated with"
        )


    # --------------------------------------------------------
    # ROLES
    # --------------------------------------------------------

    roles = _extract_values(
        candidate,
        [
            "role",
            "roles",
            "title",
            "job_title"
        ]
    )

    for role in roles:

        role_id = (
            "role:" +
            _slug(role)
        )

        _add_node(
            graph,
            role_id,
            role,
            "Role"
        )

        _add_edge(
            graph,
            person_id,
            role_id,
            "role"
        )


    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = _extract_values(
        candidate,
        [
            "project",
            "projects",
            "repositories",
            "repos"
        ]
    )

    for project in projects:

        project_id = (
            "project:" +
            _slug(project)
        )

        _add_node(
            graph,
            project_id,
            project,
            "Project"
        )

        _add_edge(
            graph,
            person_id,
            project_id,
            "contributed to"
        )


    # --------------------------------------------------------
    # LOCATIONS
    # --------------------------------------------------------

    locations = _extract_values(
        candidate,
        [
            "location",
            "locations",
            "city",
            "country"
        ]
    )

    for location in locations:

        location_id = (
            "location:" +
            _slug(location)
        )

        _add_node(
            graph,
            location_id,
            location,
            "Location"
        )

        _add_edge(
            graph,
            person_id,
            location_id,
            "located in"
        )


    # ========================================================
    # PROFILE NETWORK
    # ========================================================

    for index, profile in enumerate(all_profiles):

        if not isinstance(profile, dict):
            continue

        # ----------------------------------------------------
        # Platform
        # ----------------------------------------------------

        platforms = _extract_platforms(
            profile
        )

        # ----------------------------------------------------
        # Username
        # ----------------------------------------------------

        profile_username = (
            profile.get("username")
            or profile.get("login")
            or username
        )

        profile_url = _extract_url(
            profile
        )

        # ----------------------------------------------------
        # Profile label
        # ----------------------------------------------------

        if profile_username:

            profile_label = (
                f"{platforms[0]}: "
                f"@{_text(profile_username)}"
                if platforms
                else
                f"@{_text(profile_username)}"
            )

        elif profile_url:

            profile_label = profile_url

        else:

            profile_label = (
                f"Profile {index + 1}"
            )

        profile_id = (
            "profile:" +
            _slug(
                profile_url
                or profile_label
            )
        )

        _add_node(
            graph,
            profile_id,
            profile_label,
            "Profile"
        )

        _add_edge(
            graph,
            person_id,
            profile_id,
            "profile"
        )

        # ----------------------------------------------------
        # Platform nodes
        # ----------------------------------------------------

        for platform in platforms:

            platform_id = (
                "platform:" +
                _slug(platform)
            )

            _add_node(
                graph,
                platform_id,
                platform,
                "Platform"
            )

            _add_edge(
                graph,
                profile_id,
                platform_id,
                "on"
            )

        # ----------------------------------------------------
        # Username node
        # ----------------------------------------------------

        if profile_username:

            profile_username_id = (
                "username:" +
                _slug(profile_username)
            )

            _add_node(
                graph,
                profile_username_id,
                "@" + _text(profile_username),
                "Username"
            )

            _add_edge(
                graph,
                profile_id,
                profile_username_id,
                "uses"
            )

        # ----------------------------------------------------
        # Organization
        # ----------------------------------------------------

        profile_orgs = _extract_values(
            profile,
            [
                "organization",
                "organizations",
                "company",
                "employer"
            ]
        )

        for organization in profile_orgs:

            org_id = (
                "organization:" +
                _slug(organization)
            )

            _add_node(
                graph,
                org_id,
                organization,
                "Organization"
            )

            _add_edge(
                graph,
                profile_id,
                org_id,
                "works at"
            )

        # ----------------------------------------------------
        # Role
        # ----------------------------------------------------

        profile_roles = _extract_values(
            profile,
            [
                "role",
                "roles",
                "title",
                "job_title"
            ]
        )

        for role in profile_roles:

            role_id = (
                "role:" +
                _slug(role)
            )

            _add_node(
                graph,
                role_id,
                role,
                "Role"
            )

            _add_edge(
                graph,
                profile_id,
                role_id,
                "has role"
            )

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        profile_locations = _extract_values(
            profile,
            [
                "location",
                "city",
                "country"
            ]
        )

        for location in profile_locations:

            location_id = (
                "location:" +
                _slug(location)
            )

            _add_node(
                graph,
                location_id,
                location,
                "Location"
            )

            _add_edge(
                graph,
                profile_id,
                location_id,
                "located in"
            )

        # ----------------------------------------------------
        # Projects / repositories
        # ----------------------------------------------------

        profile_projects = _extract_values(
            profile,
            [
                "project",
                "projects",
                "repository",
                "repositories",
                "repo",
                "repos"
            ]
        )

        for project in profile_projects:

            project_id = (
                "project:" +
                _slug(project)
            )

            _add_node(
                graph,
                project_id,
                project,
                "Project"
            )

            _add_edge(
                graph,
                profile_id,
                project_id,
                "contains"
            )


    # ========================================================
    # PUBLICATIONS
    # ========================================================

    for index, publication in enumerate(publications):

        if isinstance(publication, dict):

            title = (
                publication.get("title")
                or publication.get("name")
                or f"Publication {index + 1}"
            )

            venue = (
                publication.get("venue")
                or publication.get("journal")
                or publication.get("source")
            )

        else:

            title = _text(publication)
            venue = None

        publication_id = (
            "publication:" +
            _slug(title)
        )

        _add_node(
            graph,
            publication_id,
            _text(title),
            "Publication"
        )

        _add_edge(
            graph,
            person_id,
            publication_id,
            "published"
        )

        if venue:

            venue_id = (
                "source:" +
                _slug(venue)
            )

            _add_node(
                graph,
                venue_id,
                _text(venue),
                "Source"
            )

            _add_edge(
                graph,
                publication_id,
                venue_id,
                "published in"
            )


    # ========================================================
    # EVENTS
    # ========================================================

    events = _extract_values(
        candidate,
        [
            "events",
            "event",
            "activities"
        ]
    )

    for event in events:

        event_id = (
            "event:" +
            _slug(event)
        )

        _add_node(
            graph,
            event_id,
            event,
            "Event"
        )

        _add_edge(
            graph,
            person_id,
            event_id,
            "participated in"
        )


    # ========================================================
    # SOURCE NODES
    # ========================================================

    source_values = _extract_values(
        candidate,
        [
            "source",
            "sources"
        ]
    )

    for source in source_values:

        host = _url_host(source)

        label = (
            _pretty_platform(host)
            if host
            else source
        )

        source_id = (
            "source:" +
            _slug(label)
        )

        _add_node(
            graph,
            source_id,
            label,
            "Source"
        )

        _add_edge(
            graph,
            person_id,
            source_id,
            "evidence from"
        )


    # ========================================================
    # SAFETY CHECK
    # ========================================================

    if graph.number_of_nodes() == 0:

        return None

    # ========================================================
    # OUTPUT DIRECTORY
    # ========================================================

    project_root = (
        Path(__file__).resolve().parent.parent
    )

    output_dir = (
        project_root /
        "generated"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        "identity_graph_" +
        _slug(person_name) +
        ".png"
    )

    output_path = (
        output_dir /
        filename
    )

    # ========================================================
    # DRAW GRAPH
    # ========================================================

    node_colors = {

        "Person": "#38bdf8",
        "Username": "#60a5fa",
        "Platform": "#22c55e",
        "Profile": "#4ade80",
        "Alias": "#a78bfa",
        "Organization": "#f97316",
        "Role": "#facc15",
        "Project": "#fb923c",
        "Event": "#f472b6",
        "Publication": "#c084fc",
        "Location": "#2dd4bf",
        "Source": "#cbd5e1"

    }

    node_sizes = {

        "Person": 3000,
        "Username": 1800,
        "Platform": 2200,
        "Profile": 1900,
        "Alias": 1700,
        "Organization": 1900,
        "Role": 1500,
        "Project": 1800,
        "Event": 1700,
        "Publication": 1900,
        "Location": 1700,
        "Source": 1500

    }

    # --------------------------------------------------------
    # Non-linear layout
    # --------------------------------------------------------

    node_count = graph.number_of_nodes()

    if node_count == 1:

        positions = {
            list(graph.nodes())[0]: (0, 0)
        }

    else:

        positions = nx.spring_layout(
            graph,
            seed=42,
            k=1.8,
            iterations=250
        )

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    fig = plt.figure(
        figsize=(16, 10),
        facecolor="#07111d"
    )

    ax = fig.add_subplot(111)

    ax.set_facecolor(
        "#07111d"
    )

    # --------------------------------------------------------
    # Edges
    # --------------------------------------------------------

    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        edge_color="#64748b",
        width=1.5,
        alpha=0.75
    )

    # --------------------------------------------------------
    # Nodes by type
    # --------------------------------------------------------

    for node_type, color in node_colors.items():

        nodes = [
            node
            for node, data in graph.nodes(data=True)
            if data.get("node_type") == node_type
        ]

        if not nodes:
            continue

        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=nodes,
            node_color=color,
            node_size=[
                node_sizes.get(
                    node_type,
                    1600
                )
                for _ in nodes
            ],
            alpha=0.95,
            edgecolors="#ffffff",
            linewidths=1.0,
            ax=ax
        )

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    labels = {}

    for node, data in graph.nodes(data=True):

        label = _text(
            data.get("label")
        )

        if len(label) > 28:

            label = (
                label[:25] +
                "..."
            )

        labels[node] = label

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=9,
        font_color="#ffffff",
        font_weight="bold",
        ax=ax
    )

    # --------------------------------------------------------
    # Edge labels
    # --------------------------------------------------------

    if graph.number_of_edges() <= 35:

        edge_labels = {}

        for source, target, data in graph.edges(
            data=True
        ):

            relation = data.get(
                "relation",
                ""
            )

            if relation:
                edge_labels[
                    (source, target)
                ] = relation

        nx.draw_networkx_edge_labels(
            graph,
            positions,
            edge_labels=edge_labels,
            font_size=7,
            font_color="#94a3b8",
            ax=ax
        )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    ax.set_title(
        f"Identity Knowledge Graph • {person_name}",
        fontsize=20,
        color="#ffffff",
        fontweight="bold",
        pad=20
    )

    # --------------------------------------------------------
    # Subtitle
    # --------------------------------------------------------

    ax.text(
        0.5,
        1.01,
        (
            f"{graph.number_of_nodes()} entities • "
            f"{graph.number_of_edges()} relationships"
        ),
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=10,
        color="#94a3b8"
    )

    ax.axis(
        "off"
    )

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    from matplotlib.lines import Line2D

    legend_items = []

    for node_type, color in node_colors.items():

        if any(
            data.get("node_type") == node_type
            for _, data in graph.nodes(data=True)
        ):

            legend_items.append(
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="none",
                    markerfacecolor=color,
                    markeredgecolor="white",
                    markersize=9,
                    label=node_type
                )
            )

    if legend_items:

        ax.legend(
            handles=legend_items,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.02),
            ncol=4,
            frameon=False,
            labelcolor="white",
            fontsize=9
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    plt.tight_layout()

    fig.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
        facecolor=fig.get_facecolor()
    )

    plt.close(fig)

    return str(output_path)