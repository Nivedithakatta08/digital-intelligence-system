def validate_image(image):
    """
    Validate an uploaded image.

    Supports Streamlit UploadedFile,
    bytes, and file-like objects.
    """

    if image is None:
        return {
            "valid": False,
            "error": "No image was provided."
        }

    try:

        if isinstance(image, bytes):

            if len(image) == 0:
                return {
                    "valid": False,
                    "error": "The image is empty."
                }

            return {
                "valid": True,
                "error": None
            }


        if hasattr(image, "getvalue"):

            data = image.getvalue()

            if not data:

                return {
                    "valid": False,
                    "error": "The uploaded image is empty."
                }

            return {
                "valid": True,
                "error": None
            }


        if hasattr(image, "read"):

            try:
                position = image.tell()
            except Exception:
                position = None


            data = image.read()


            if position is not None:

                try:
                    image.seek(position)
                except Exception:
                    pass


            if not data:

                return {
                    "valid": False,
                    "error": "The uploaded image is empty."
                }


            return {
                "valid": True,
                "error": None
            }


    except Exception as error:

        return {
            "valid": False,
            "error": f"Unable to read image: {error}"
        }


    return {
        "valid": False,
        "error": "Unsupported image input."
    }


# =========================================================
# IMAGE → BYTES
# =========================================================

def image_to_bytes(image):
    """
    Convert an uploaded image into raw bytes.
    """

    if image is None:

        raise ValueError(
            "No image was provided."
        )


    if isinstance(image, bytes):

        if not image:

            raise ValueError(
                "The image is empty."
            )

        return image


    if hasattr(image, "getvalue"):

        data = image.getvalue()

        if not data:

            raise ValueError(
                "The uploaded image is empty."
            )

        return data


    if hasattr(image, "read"):

        try:
            position = image.tell()
        except Exception:
            position = None


        data = image.read()


        if position is not None:

            try:
                image.seek(position)
            except Exception:
                pass


        if not data:

            raise ValueError(
                "The uploaded image is empty."
            )

        return data


    raise ValueError(
        "Unsupported image input."
    )


# =========================================================
# IMAGE METADATA
# =========================================================

def get_image_metadata(image):
    """
    Return basic metadata about the uploaded image.
    """

    try:

        data = image_to_bytes(
            image
        )

        content_type = None

        if hasattr(image, "type"):

            content_type = image.type


        return {
            "size_bytes": len(data),
            "content_type": content_type
        }


    except Exception as error:

        return {
            "size_bytes": 0,
            "content_type": None,
            "error": str(error)
        }


# =========================================================
# IMAGE IDENTITY DISCOVERY
# =========================================================

def discover_identity_from_image(image):
    """
    Image-to-public-identity discovery interface.

    This function validates and prepares the image.

    A real image identity discovery provider can be
    connected here later.

    IMPORTANT:
    This function does not invent an identity when
    no provider has returned one.
    """

    validation = validate_image(
        image
    )


    if not validation["valid"]:

        return {
            "success": False,
            "candidates": [],
            "metadata": {},
            "error": validation["error"]
        }


    try:

        metadata = get_image_metadata(
            image
        )

    except Exception as error:

        return {
            "success": False,
            "candidates": [],
            "metadata": {},
            "error": (
                "Image processing failed: "
                f"{error}"
            )
        }


    # -----------------------------------------------------
    # REAL IMAGE IDENTITY PROVIDER
    # -----------------------------------------------------
    #
    # This is where a real image-to-identity API/provider
    # will eventually be connected.
    #
    # Expected candidate format:
    #
    # {
    #     "name": "Example Person",
    #     "username": "example_user",
    #     "organization": "Example Organization",
    #     "location": "Example Location",
    #     "profile_url": "https://example.com/profile",
    #     "source": "image_identity_provider",
    #     "image_match_score": 0.87
    # }
    #
    # We intentionally return no candidate until an actual
    # provider is connected.
    # -----------------------------------------------------

    return {
        "success": False,
        "candidates": [],
        "metadata": metadata,
        "error": (
            "No image-to-identity provider is connected yet."
        )
    }


# =========================================================
# NORMALIZE IMAGE CANDIDATES
# =========================================================

def normalize_image_candidates(candidates):
    """
    Convert candidates returned by an image identity
    provider into the common profile format used by
    the rest of the application.
    """

    if not candidates:

        return []


    if isinstance(candidates, dict):

        candidates = [
            candidates
        ]


    normalized = []


    for candidate in candidates:

        if not isinstance(candidate, dict):

            continue


        profile = {
            "source": candidate.get(
                "source",
                "image_identity_provider"
            ),

            "name": candidate.get(
                "name"
            ),

            "username": candidate.get(
                "username"
            ),

            "organization": candidate.get(
                "organization"
            ),

            "location": candidate.get(
                "location"
            ),

            "bio": candidate.get(
                "bio"
            ),

            "profile_url": candidate.get(
                "profile_url"
            )
        }


        image_score = candidate.get(
            "image_match_score"
        )


        if image_score is not None:

            try:

                profile[
                    "image_match_score"
                ] = float(
                    image_score
                )

            except (
                TypeError,
                ValueError
            ):

                pass


        # Remove empty fields.

        profile = {
            key: value
            for key, value in profile.items()
            if value not in (
                None,
                "",
                []
            )
        }


        if (
            profile.get("name")
            or profile.get("username")
        ):

            normalized.append(
                profile
            )


    return normalized