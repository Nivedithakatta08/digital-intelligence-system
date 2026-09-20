import json
import os

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


model = None


if (
    GEMINI_API_KEY
    and genai is not None
):

    try:

        genai.configure(
            api_key=GEMINI_API_KEY
        )

        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

    except Exception:

        model = None


# =========================================================
# ENTITY EXTRACTION
# =========================================================

def extract_entities(
    text
):
    """
    Extract useful public-identity entities from text.

    If Gemini is unavailable, return a safe empty result.
    """

    if not text:

        return {}


    if model is None:

        return {
            "status": (
                "Entity extraction unavailable"
            ),

            "message": (
                "Configure GEMINI_API_KEY to enable "
                "AI-assisted entity extraction."
            )
        }


    prompt = f"""
Extract structured public-identity information from
the following text.

Return ONLY valid JSON.

Use these fields:

{{
    "people": [],
    "organizations": [],
    "roles": [],
    "projects": [],
    "events": [],
    "locations": [],
    "technologies": []
}}

Do not invent information.

Text:
{text}
"""


    try:

        response = model.generate_content(
            prompt
        )


        raw = response.text.strip()


        # Remove accidental markdown fences.

        if raw.startswith(
            "```"
        ):

            raw = raw.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()


        return json.loads(
            raw
        )


    except Exception as error:

        return {
            "status": "Extraction failed",
            "error": str(
                error
            )
        }