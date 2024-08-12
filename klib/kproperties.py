import re


def ekv(s: str) -> tuple[str, str] | None:
    """
    Extracts a key and a value from a string of the format key="value".

    Args:
        s (str): The input string.

    Returns:
        tuple[str, str] | None: A tuple containing the key and value if the format is correct, otherwise None.
    """
    # Regex pattern to match key="value"
    pattern = r'([^=]+)="([^"]*)"'

    # Search for matches
    match = re.match(pattern, s)

    if match:
        # Extract key and value
        key = match.group(1).strip()
        value = match.group(2)
        return key, value
    else:
        return None


def parse_properties(properties: str):
    props = {}
    for line in properties.split("\n"):
        props[ekv(line)[0]] = ekv(line)[1]
    return props


if __name__ == '__main__':
    p = parse_properties("""1="a"
    2="b\"""")
    print(p)
