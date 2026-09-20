import json


def get_mock_profiles():

    with open(
        "data/mock_profiles.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)