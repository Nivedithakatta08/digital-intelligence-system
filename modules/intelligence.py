import re


# ============================================================
# HELPERS
# ============================================================

def as_list(value):

    if value is None:
        return []

    if isinstance(
        value,
        list
    ):
        return [
            item
            for item in value
            if item not in (None, "")
        ]

    return [value]


def unique_values(values):

    result = []
    seen = set()

    for value in values:

        if value is None:
            continue

        text = str(
            value
        ).strip()

        if not text:
            continue

        key = text.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(
            text
        )

    return result


# ============================================================
# TEXT ENTITY EXTRACTION
# ============================================================

def extract_text_entities(
    text
):

    if not text:
        return {}

    text = str(
        text
    )

    entities = {}

    # --------------------------------------------------------
    # Simple keyword-based extraction
    # --------------------------------------------------------

    role_keywords = [
        "engineer",
        "developer",
        "researcher",
        "scientist",
        "manager",
        "designer",
        "student",
        "professor",
        "founder",
        "analyst"
    ]

    roles = []

    for keyword in role_keywords:

        pattern = (
            r"\b"
            r"([A-Za-z][A-Za-z\s-]{0,40})"
            r"\b"
            + re.escape(keyword)
        )

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            value = (
                str(match).strip()
                + " "
                + keyword
            )

            value = re.sub(
                r"\s+",
                " ",
                value
            ).strip()

            if len(value) < 80:
                roles.append(
                    value
                )

    if roles:

        entities["roles"] = unique_values(
            roles
        )

    return entities


# ============================================================
# PUBLICATION MATCH
# ============================================================

def publication_matches_profile(
    publication,
    profile_name,
    usernames
):

    if not isinstance(
        publication,
        dict
    ):
        return False

    authors = publication.get(
        "authors",
        []
    )

    if not isinstance(
        authors,
        list
    ):
        authors = [
            authors
        ]

    search_terms = [
        str(profile_name).lower()
    ]

    search_terms.extend(
        str(username).lower()
        for username in usernames
        if username
    )

    for author in authors:

        author_text = str(
            author
        ).lower()

        for term in search_terms:

            if not term:
                continue

            if term in author_text:
                return True

    return False


# ============================================================
# BUILD INTELLIGENCE
# ============================================================

def build_intelligence(
    profile,
    publications=None,
    evidence=None,
    conflicts=None,
    timeline=None
):

    if not isinstance(
        profile,
        dict
    ):

        return {
            "profile": {},
            "summary": {},
            "entities": {},
            "publications": [],
            "evidence": [],
            "conflicts": [],
            "timeline": []
        }

    publications = (
        publications
        if isinstance(
            publications,
            list
        )
        else []
    )

    evidence = (
        evidence
        if isinstance(
            evidence,
            list
        )
        else []
    )

    conflicts = (
        conflicts
        if isinstance(
            conflicts,
            list
        )
        else []
    )

    timeline = (
        timeline
        if isinstance(
            timeline,
            list
        )
        else []
    )

    profile_name = (
        profile.get("resolved_name")
        or profile.get("name")
        or profile.get("username")
        or "Unknown"
    )

    usernames = as_list(
        profile.get(
            "usernames"
        )
    )

    username = profile.get(
        "username"
    )

    if username:
        usernames.append(
            username
        )

    # --------------------------------------------------------
    # Structured entities
    # --------------------------------------------------------

    entities = {}

    field_map = {
        "Aliases": "aliases",
        "Usernames": "usernames",
        "Organizations": "organizations",
        "Roles": "roles",
        "Projects": "projects",
        "Events": "events",
        "Locations": "locations"
    }

    for label, field in field_map.items():

        value = profile.get(
            field
        )

        if value is None:

            # Singular fallbacks

            singular_map = {
                "organizations": "organization",
                "locations": "location"
            }

            fallback = singular_map.get(
                field
            )

            if fallback:

                value = profile.get(
                    fallback
                )

        values = unique_values(
            as_list(value)
        )

        if values:

            entities[label] = values

    # --------------------------------------------------------
    # Bio-derived entities
    # --------------------------------------------------------

    bio = profile.get(
        "bio"
    )

    extracted = extract_text_entities(
        bio
    )

    for key, values in extracted.items():

        if key == "roles":

            existing = entities.get(
                "Roles",
                []
            )

            entities["Roles"] = unique_values(
                existing + values
            )

    # --------------------------------------------------------
    # Publications
    # --------------------------------------------------------

    matched_publications = []

    for publication in publications:

        if publication_matches_profile(
            publication,
            profile_name,
            usernames
        ):

            matched_publications.append(
                publication
            )

    # --------------------------------------------------------
    # Profile-specific evidence
    # --------------------------------------------------------

    candidate_id = profile.get(
        "candidate_id"
    )

    profile_evidence = []

    for item in evidence:

        if not isinstance(
            item,
            dict
        ):
            continue

        item_candidate = item.get(
            "candidate_id"
        )

        if (
            candidate_id
            and item_candidate
            and str(candidate_id)
            != str(item_candidate)
        ):
            continue

        profile_evidence.append(
            item
        )

    # --------------------------------------------------------
    # Profile-specific conflicts
    # --------------------------------------------------------

    profile_conflicts = []

    for conflict in conflicts:

        if isinstance(
            conflict,
            dict
        ):
            profile_conflicts.append(
                conflict
            )

    # --------------------------------------------------------
    # Profile-specific timeline
    # --------------------------------------------------------

    profile_timeline = []

    for event in timeline:

        if isinstance(
            event,
            dict
        ):
            profile_timeline.append(
                event
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {
        "profile_name": profile_name,
        "confidence": profile.get(
            "confidence",
            0
        ),
        "publication_count": len(
            matched_publications
        ),
        "evidence_count": len(
            profile_evidence
        ),
        "conflict_count": len(
            profile_conflicts
        ),
        "timeline_event_count": len(
            profile_timeline
        ),
        "entity_count": sum(
            len(values)
            for values in entities.values()
        )
    }

    # --------------------------------------------------------
    # Readable profile
    # --------------------------------------------------------

    readable_profile = {
        "name": profile_name,
        "username": profile.get(
            "username"
        ),
        "aliases": as_list(
            profile.get("aliases")
        ),
        "usernames": unique_values(
            usernames
        ),
        "organizations": unique_values(
            as_list(
                profile.get(
                    "organizations"
                    or "organization"
                )
            )
        ),
        "roles": unique_values(
            as_list(
                profile.get("roles")
            )
        ),
        "projects": unique_values(
            as_list(
                profile.get("projects")
            )
        ),
        "events": unique_values(
            as_list(
                profile.get("events")
            )
        ),
        "locations": unique_values(
            as_list(
                profile.get(
                    "locations"
                    or "location"
                )
            )
        ),
        "sources": unique_values(
            as_list(
                profile.get(
                    "sources"
                    or "source"
                )
            )
        )
    }

    return {
        "profile": readable_profile,
        "summary": summary,
        "entities": entities,
        "publications": matched_publications,
        "evidence": profile_evidence,
        "conflicts": profile_conflicts,
        "timeline": profile_timeline
    }