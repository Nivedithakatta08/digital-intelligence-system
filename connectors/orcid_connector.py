import requests


def search_orcid(name):

    url = "https://pub.orcid.org/v3.0/expanded-search/"

    headers = {
        "Accept": "application/json"
    }

    params = {
        "q": name
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        print("ORCID STATUS:", response.status_code)

        if response.status_code != 200:
            return []

        data = response.json()

        profiles = []

        for result in data.get("expanded-result", [])[:5]:

            profiles.append({
                "source": "orcid",
                "name": (
                    f"{result.get('given-names', '')} "
                    f"{result.get('family-names', '')}"
                ).strip(),
                "username": result.get("orcid-id"),
                "organization": result.get(
                    "institution-name"
                ),
                "bio": None,
                "location": None,
                "profile_url": (
                    f"https://orcid.org/"
                    f"{result.get('orcid-id')}"
                )
            })

        return profiles

    except Exception as e:

        print("ORCID ERROR:", e)

        return []