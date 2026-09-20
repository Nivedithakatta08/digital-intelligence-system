import os

from modules.candidate_index import (
    build_candidate_index,
    get_candidates_with_images
)

from modules.image_embeddings import (
    create_embedding
)

from modules.image_matcher import (
    match_candidates,
    get_best_match
)


# ---------------------------------------------------------
# IMAGE VALIDATION
# ---------------------------------------------------------

def validate_image(image):
    """
    Basic validation for an uploaded image.
    """

    if image is None:
        return {
            "valid": False,
            "error": "No image was provided."
        }

    return {
        "valid": True,
        "error": None
    }


# ---------------------------------------------------------
# BUILD CANDIDATE INDEX
# ---------------------------------------------------------

def load_image_candidates():
    """
    Load candidates that have an image available
    for face-based matching.
    """

    candidates = get_candidates_with_images()

    return candidates


# ---------------------------------------------------------
# RUN IMAGE MATCHING
# ---------------------------------------------------------

def run_image_matching(
    image,
    top_k=5
):
    """
    Run the complete image-matching pipeline.

    Steps:

    1. Validate uploaded image
    2. Generate query face embedding
    3. Load candidate image index
    4. Compare query against candidates
    5. Sort candidates by similarity
    6. Return the best candidate and rankings
    """

    validation = validate_image(
        image
    )

    if not validation["valid"]:

        return {
            "success": False,
            "error": validation["error"],
            "query_embedding": None,
            "candidates": [],
            "best_match": None,
            "candidate_count": 0
        }

    # -----------------------------------------------------
    # STEP 1: CREATE QUERY EMBEDDING
    # -----------------------------------------------------

    try:

        query_embedding = create_embedding(
            image
        )

    except Exception as e:

        return {
            "success": False,
            "error": (
                f"Unable to process the uploaded image: {e}"
            ),
            "query_embedding": None,
            "candidates": [],
            "best_match": None,
            "candidate_count": 0
        }

    # -----------------------------------------------------
    # STEP 2: LOAD CANDIDATES
    # -----------------------------------------------------

    try:

        candidates = load_image_candidates()

    except Exception as e:

        return {
            "success": False,
            "error": (
                f"Unable to load candidate images: {e}"
            ),
            "query_embedding": None,
            "candidates": [],
            "best_match": None,
            "candidate_count": 0
        }

    if not candidates:

        return {
            "success": False,
            "error": (
                "No candidate images are available. "
                "Add images to data/candidate_images/."
            ),
            "query_embedding": query_embedding,
            "candidates": [],
            "best_match": None,
            "candidate_count": 0
        }

    # -----------------------------------------------------
    # STEP 3: MATCH AGAINST CANDIDATES
    # -----------------------------------------------------

    results = match_candidates(
        query_embedding=query_embedding,
        candidates=candidates,
        top_k=top_k
    )

    # -----------------------------------------------------
    # STEP 4: FIND BEST MATCH
    # -----------------------------------------------------

    best_match = get_best_match(
        results
    )

    # -----------------------------------------------------
    # STEP 5: RETURN COMPLETE RESULT
    # -----------------------------------------------------

    return {
        "success": bool(results),

        "error": None
        if results
        else "No candidates could be compared.",

        "query_embedding": query_embedding,

        "candidates": results,

        "best_match": best_match,

        "candidate_count": len(
            candidates
        ),

        "matched_count": len(
            results
        )
    }


# ---------------------------------------------------------
# REMOVE EMBEDDING FROM DISPLAY RESULT
# ---------------------------------------------------------

def prepare_result_for_display(
    result
):
    """
    Create a Streamlit-friendly result without
    exposing the raw embedding tensor.
    """

    if not isinstance(
        result,
        dict
    ):
        return {}

    cleaned = dict(
        result
    )

    cleaned.pop(
        "query_embedding",
        None
    )

    return cleaned


# ---------------------------------------------------------
# GET BEST PUBLIC PROFILE
# ---------------------------------------------------------

def get_best_public_profile(
    result
):
    """
    Extract the public profile information associated
    with the highest-scoring candidate.
    """

    if not isinstance(
        result,
        dict
    ):
        return None

    best_match = result.get(
        "best_match"
    )

    if not isinstance(
        best_match,
        dict
    ):
        return None

    profiles = best_match.get(
        "profiles",
        []
    )

    if not profiles:
        return None

    if isinstance(
        profiles,
        list
    ):
        for profile in profiles:

            if isinstance(
                profile,
                dict
            ):
                return profile

    return None


# ---------------------------------------------------------
# PIPELINE SUMMARY
# ---------------------------------------------------------

def get_image_matching_summary(
    result
):
    """
    Return a compact summary suitable for
    the Streamlit interface and final report.
    """

    if not isinstance(
        result,
        dict
    ):
        return {
            "success": False,
            "message": "Invalid pipeline result."
        }

    best_match = result.get(
        "best_match"
    )

    if not best_match:

        return {
            "success": False,
            "message": result.get(
                "error",
                "No matching candidate found."
            ),
            "candidate_count": result.get(
                "candidate_count",
                0
            ),
            "matched_count": result.get(
                "matched_count",
                0
            )
        }

    profiles = best_match.get(
        "profiles",
        []
    )

    best_profile = None

    if profiles:

        for profile in profiles:

            if isinstance(
                profile,
                dict
            ):

                best_profile = profile
                break

    return {
        "success": True,

        "candidate_id": best_match.get(
            "candidate_id"
        ),

        "similarity": best_match.get(
            "similarity"
        ),

        "similarity_percentage": best_match.get(
            "similarity_percentage"
        ),

        "classification": best_match.get(
            "classification"
        ),

        "name": (
            best_profile.get("name")
            if best_profile
            else None
        ),

        "username": (
            best_profile.get("username")
            if best_profile
            else None
        ),

        "organization": (
            best_profile.get("organization")
            if best_profile
            else None
        ),

        "candidate_count": result.get(
            "candidate_count",
            0
        ),

        "matched_count": result.get(
            "matched_count",
            0
        )
    }