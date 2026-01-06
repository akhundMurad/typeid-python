from typeid.core.errors import InvalidTypeIDStringException


def get_prefix_and_suffix(string: str) -> tuple:
    parts = string.rsplit("_", 1)

    # When there's no underscore in the string.
    if len(parts) == 1:
        if parts[0].strip() == "":
            raise InvalidTypeIDStringException(f"Invalid TypeID: {string}")
        return None, parts[0]

    # When there is an underscore, unpack prefix and suffix.
    prefix, suffix = parts
    if prefix.strip() == "" or suffix.strip() == "":
        raise InvalidTypeIDStringException(f"Invalid TypeID: {string}")

    return prefix, suffix
