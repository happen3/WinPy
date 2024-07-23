import re


def parse(command: str) -> list[str]:
    """Command Parser, parses a command string into a list of arguments."""
    # Regular expression to match spaces outside of quotes
    args = re.findall(r'"([^"]*)"|(\S+)', command)
    # Extracting non-empty groups from the regex matches
    args = [group[0] or group[1] for group in args]
    return args


def verify(parsed_structure: list[str]) -> bool:
    """Verifies a command structure generated using `parse()` using special criteria."""
    banned_characters = ["{", "}", "(", ")", "[", "]", ";", "|", "&"]
    if parsed_structure[0].startswith('"') or parsed_structure[0].startswith('\''):
        return False
    for char in banned_characters:
        if char in parsed_structure[0]:
            return False
    else:
        return True


if __name__ == '__main__':
    cmd = "help kcrypto kaes \"How to use?\""
    print(parse(cmd), verify(parse(cmd)))
