def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate that a generated SQL query is read-only.

    Returns:
        (True, "Query is valid") when the query is safe.
        (False, reason) when the query should be rejected.
    """

    # Remove leading/trailing whitespace
    cleaned_sql = sql.strip()

    # Reject an empty query
    if not cleaned_sql:
        return False, "Query is empty."

    # Remove a trailing semicolon for easier validation
    cleaned_sql = cleaned_sql.rstrip(";").strip()

    # Reject multiple SQL statements
    if ";" in cleaned_sql:
        return False, "Multiple SQL statements are not allowed."

    # Get the first SQL keyword
    first_keyword = cleaned_sql.split()[0].upper()

    # Only SELECT statements are allowed
    if first_keyword != "SELECT":
        return False, f"Only SELECT statements are allowed. Found: {first_keyword}"

    return True, "Query is valid."
