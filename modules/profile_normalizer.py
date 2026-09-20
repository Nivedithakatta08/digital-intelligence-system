def normalize_profile(profile):

    normalized = {
        "source": str(profile.get("source", "")),
        "name": profile.get("name"),
        "username": profile.get("username"),
        "organization": profile.get("organization"),
        "bio": profile.get("bio"),
        "location": profile.get("location"),
        "profile_url": profile.get("profile_url")
    }

    for key, value in normalized.items():

        if value is None:
            normalized[key] = ""

        elif isinstance(value, list):

            normalized[key] = ", ".join(
                str(v)
                for v in value
                if v
            )

        else:

            normalized[key] = str(value)

    return normalized


def normalize_profiles(profiles):

    return [
        normalize_profile(profile)
        for profile in profiles
    ]