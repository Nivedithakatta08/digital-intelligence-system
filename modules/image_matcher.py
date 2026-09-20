import os

import torch
import torch.nn.functional as F

from modules.image_embeddings import create_embedding


# ---------------------------------------------------------
# SIMILARITY
# ---------------------------------------------------------

def cosine_similarity(
    embedding_a,
    embedding_b
):
    """
    Calculate cosine similarity between two embeddings.

    Returns:
        float between -1 and 1
    """

    if embedding_a is None or embedding_b is None:
        return 0.0

    if not isinstance(
        embedding_a,
        torch.Tensor
    ):
        embedding_a = torch.tensor(
            embedding_a,
            dtype=torch.float32
        )

    if not isinstance(
        embedding_b,
        torch.Tensor
    ):
        embedding_b = torch.tensor(
            embedding_b,
            dtype=torch.float32
        )

    embedding_a = F.normalize(
        embedding_a,
        p=2,
        dim=0
    )

    embedding_b = F.normalize(
        embedding_b,
        p=2,
        dim=0
    )

    similarity = torch.dot(
        embedding_a,
        embedding_b
    )

    return float(
        similarity.item()
    )


# ---------------------------------------------------------
# SIMILARITY SCORE
# ---------------------------------------------------------

def similarity_percentage(
    similarity
):
    """
    Convert cosine similarity into a simple
    0-100 display score.

    This is a similarity score, NOT an identity probability.
    """

    similarity = max(
        -1.0,
        min(1.0, float(similarity))
    )

    percentage = (
        (similarity + 1.0)
        / 2.0
        * 100.0
    )

    return round(
        percentage,
        2
    )


# ---------------------------------------------------------
# MATCH LABEL
# ---------------------------------------------------------

def classify_similarity(
    similarity
):
    """
    Give a human-readable similarity category.

    These thresholds are prototype thresholds.
    They should be calibrated with validation data
    before being used for real-world identity decisions.
    """

    similarity = float(
        similarity
    )

    if similarity >= 0.75:
        return "High similarity"

    if similarity >= 0.60:
        return "Moderate similarity"

    if similarity >= 0.45:
        return "Low similarity"

    return "Very low similarity"


# ---------------------------------------------------------
# SINGLE CANDIDATE MATCH
# ---------------------------------------------------------

def match_candidate(
    query_embedding,
    candidate
):
    """
    Compare the query embedding with one candidate.

    Returns a result dictionary.
    """

    if not isinstance(
        candidate,
        dict
    ):
        return None

    candidate_id = candidate.get(
        "candidate_id"
    )

    image_path = candidate.get(
        "image_path"
    )

    if not candidate_id:
        return None

    if not image_path:
        return None

    if not os.path.exists(
        image_path
    ):
        return None

    try:

        candidate_embedding = create_embedding(
            image_path
        )

        similarity = cosine_similarity(
            query_embedding,
            candidate_embedding
        )

    except Exception as e:

        return {
            "candidate_id": candidate_id,
            "similarity": 0.0,
            "similarity_percentage": 0.0,
            "classification": "Unable to compare",
            "image_path": image_path,
            "profiles": candidate.get(
                "profiles",
                []
            ),
            "error": str(e)
        }

    return {
        "candidate_id": candidate_id,

        "similarity": round(
            similarity,
            6
        ),

        "similarity_percentage": similarity_percentage(
            similarity
        ),

        "classification": classify_similarity(
            similarity
        ),

        "image_path": image_path,

        "profiles": candidate.get(
            "profiles",
            []
        )
    }


# ---------------------------------------------------------
# MATCH ALL CANDIDATES
# ---------------------------------------------------------

def match_candidates(
    query_embedding,
    candidates,
    top_k=5
):
    """
    Compare the query embedding against all
    available candidate images.

    Returns:
        candidates sorted from highest similarity
        to lowest similarity.
    """

    if query_embedding is None:
        return []

    if not candidates:
        return []

    results = []

    for candidate in candidates:

        result = match_candidate(
            query_embedding,
            candidate
        )

        if result is None:
            continue

        # Skip failed comparisons.
        if result.get(
            "classification"
        ) == "Unable to compare":

            continue

        results.append(
            result
        )

    results.sort(
        key=lambda item: item.get(
            "similarity",
            0.0
        ),
        reverse=True
    )

    return results[:top_k]


# ---------------------------------------------------------
# BEST MATCH
# ---------------------------------------------------------

def get_best_match(
    results
):
    """
    Return the highest-scoring candidate.

    Returns None if no candidates were matched.
    """

    if not results:
        return None

    return results[0]