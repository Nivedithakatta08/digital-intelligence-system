import json
import os


PROFILES_PATH = "data/mock_profiles.json"
IMAGE_DIRECTORY = "data/candidate_images"


def load_profiles():
    """
    Load candidate profiles from the mock profile dataset.
    """

    if not os.path.exists(PROFILES_PATH):
        return []

    try:

        with open(
            PROFILES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):
        return []

    if not isinstance(data, list):
        return []

    return data


def get_candidate_profiles():
    """
    Group platform profiles by candidate_id.

    Multiple public profiles can belong to the same
    candidate/person.
    """

    profiles = load_profiles()

    candidates = {}

    for profile in profiles:

        if not isinstance(profile, dict):
            continue

        candidate_id = profile.get(
            "candidate_id"
        )

        if not candidate_id:
            continue

        if candidate_id not in candidates:

            candidates[candidate_id] = {
                "candidate_id": candidate_id,
                "profiles": []
            }

        candidates[candidate_id]["profiles"].append(
            profile
        )

    return list(
        candidates.values()
    )


def get_candidate_image_path(
    candidate_id
):
    """
    Return the expected image path for a candidate.
    """

    if not candidate_id:
        return None

    filename = (
        f"{candidate_id}.jpg"
    )

    path = os.path.join(
        IMAGE_DIRECTORY,
        filename
    )

    if os.path.exists(path):
        return path

    # Also check PNG.
    filename = (
        f"{candidate_id}.png"
    )

    path = os.path.join(
        IMAGE_DIRECTORY,
        filename
    )

    if os.path.exists(path):
        return path

    return None


def build_candidate_index():
    """
    Build a simple candidate index containing:

    candidate_id
    public profiles
    candidate image path
    """

    candidates = get_candidate_profiles()

    index = []

    for candidate in candidates:

        candidate_id = candidate.get(
            "candidate_id"
        )

        image_path = get_candidate_image_path(
            candidate_id
        )

        index.append({

            "candidate_id": candidate_id,

            "profiles": candidate.get(
                "profiles",
                []
            ),

            "image_path": image_path,

            "has_image": bool(
                image_path
            )
        })

    return index


def get_candidates_with_images():
    """
    Return only candidates that have an image available
    for image-based matching.
    """

    index = build_candidate_index()

    return [
        candidate
        for candidate in index
        if candidate.get("has_image")
    ]