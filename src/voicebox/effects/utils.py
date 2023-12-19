def db(db_: float) -> float:
    """
    Convert decibels to gain. Examples:

    - ``db(0) -> 1``
    - ``db(-6) -> 0.501``
    - ``db(+6) -> 1.995``
    """

    return 10 ** (db_ / 20)
