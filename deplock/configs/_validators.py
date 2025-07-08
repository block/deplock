

def is_float_string(s: str) -> str:
    try:
        float(s)
    except ValueError:
        raise
    return s