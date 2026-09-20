import requests


def search_crossref(name):
    """
    Search Crossref for publications associated with a person's name.

    Returns publication records, not person profiles.
    """

    url = "https://api.crossref.org/works"

    try:
        response = requests.get(
            url,
            params={
                "query.author": name,
                "rows": 5
            },
            timeout=10
        )

        print("CROSSREF STATUS:", response.status_code)

        if response.status_code != 200:
            return []

        data = response.json()

        publications = []

        for item in data.get("message", {}).get("items", []):
            title_list = item.get("title", [])

            title = title_list[0] if title_list else ""

            authors = []

            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")

                full_name = f"{given} {family}".strip()

                if full_name:
                    authors.append(full_name)

            publication = {
                "entity_type": "publication",
                "source": "crossref",
                "title": title,
                "authors": authors,
                "published": item.get("published-print")
                or item.get("published-online"),
                "doi": item.get("DOI"),
                "profile_url": item.get("URL")
            }

            publications.append(publication)

        return publications

    except Exception as e:
        print("CROSSREF ERROR:", e)
        return []