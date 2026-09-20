import os

import torch
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN


# ---------------------------------------------------------
# MODEL INITIALIZATION
# ---------------------------------------------------------

_device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

_face_detector = None
_embedding_model = None


def load_models():
    """
    Load the face detector and face embedding model once.
    """

    global _face_detector
    global _embedding_model

    if _face_detector is None:

        _face_detector = MTCNN(
            image_size=160,
            margin=20,
            keep_all=False,
            post_process=True,
            device=_device
        )

    if _embedding_model is None:

        _embedding_model = InceptionResnetV1(
            pretrained="vggface2"
        ).eval().to(_device)

    return (
        _face_detector,
        _embedding_model
    )


# ---------------------------------------------------------
# IMAGE LOADING
# ---------------------------------------------------------

def load_image(image):
    """
    Load an image from a path, uploaded file, or PIL image.
    """

    if image is None:
        raise ValueError(
            "Image is required."
        )

    if isinstance(
        image,
        Image.Image
    ):

        return image.convert("RGB")

    if isinstance(
        image,
        (str, os.PathLike)
    ):

        if not os.path.exists(image):
            raise FileNotFoundError(
                f"Image not found: {image}"
            )

        return Image.open(
            image
        ).convert("RGB")

    try:

        return Image.open(
            image
        ).convert("RGB")

    except Exception as e:

        raise ValueError(
            f"Unable to read image: {e}"
        )


# ---------------------------------------------------------
# FACE EMBEDDING
# ---------------------------------------------------------

def create_embedding(image):
    """
    Detect a face and generate a face embedding.

    Returns:
        normalized PyTorch tensor

    Raises:
        ValueError if no face is detected.
    """

    face_detector, embedding_model = load_models()

    image = load_image(
        image
    )

    face = face_detector(
        image
    )

    if face is None:

        raise ValueError(
            "No detectable face was found in the image."
        )

    face = face.unsqueeze(
        0
    ).to(_device)

    with torch.no_grad():

        embedding = embedding_model(
            face
        )

    embedding = torch.nn.functional.normalize(
        embedding,
        p=2,
        dim=1
    )

    return embedding.squeeze(
        0
    )


# ---------------------------------------------------------
# EMBEDDING SERIALIZATION
# ---------------------------------------------------------

def embedding_to_list(
    embedding
):
    """
    Convert a PyTorch tensor embedding
    into a normal Python list.
    """

    if embedding is None:
        return []

    if not isinstance(
        embedding,
        torch.Tensor
    ):

        embedding = torch.tensor(
            embedding,
            dtype=torch.float32
        )

    return (
        embedding
        .detach()
        .cpu()
        .tolist()
    )


def list_to_embedding(
    values
):
    """
    Convert a stored list back into
    a PyTorch tensor.
    """

    if not values:

        return None

    embedding = torch.tensor(
        values,
        dtype=torch.float32
    )

    return torch.nn.functional.normalize(
        embedding,
        p=2,
        dim=0
    )