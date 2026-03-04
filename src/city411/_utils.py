"""Utilities."""

def id_generator(stem, digits):
    """Generate unique IDs of the form 'stemDDDD'."""
    i = 1
    while True:
        temp = str(i)
        assert len(temp) <= digits, f"ID generation overflow {stem}: {i}"
        yield f"{stem}{temp.zfill(digits)}"
        i += 1


def validate(cond, msg):
    """Validate a condition."""
    if not cond:
        raise ValueError(msg)
