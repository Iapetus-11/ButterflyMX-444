
def parse_bool(text: str | None) -> bool:
    if (text or '').lower() == "true":
        return True

    return False
