import re


# SQL operations that should never be allowed.
FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "ATTACH",
    "DETACH",
    "COPY",
    "EXPORT",
    "IMPORT",
    "INSTALL",
    "LOAD",
    "CALL",
}


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate that a generated SQL query is read-only.

    Returns:
        (True, "Query is valid") when the query is safe.
        (False, reason) when the query should be rejected.
    """

    if not isinstance(sql, str):
        return False, "SQL query must be a string."

    # Remove leading/trailing whitespace.
    cleaned_sql = sql.strip()

    # Reject empty queries.
    if not cleaned_sql:
        return False, "Query is empty."

    # Remove markdown code fences if the LLM accidentally returns them.
    cleaned_sql = re.sub(r"^```(?:sql)?\s*", "", cleaned_sql, flags=re.IGNORECASE)
    cleaned_sql = re.sub(r"\s*```$", "", cleaned_sql).strip()

    if not cleaned_sql:
        return False, "Query is empty."

    # Only allow one SQL statement.
    # A single trailing semicolon is acceptable.
    without_trailing_semicolon = cleaned_sql.rstrip(";").strip()

    if ";" in without_trailing_semicolon:
        return False, "Multiple SQL statements are not allowed."

    cleaned_sql = without_trailing_semicolon

    # Remove SQL comments before checking keywords.
    no_comments = re.sub(r"/\*.*?\*/", " ", cleaned_sql, flags=re.DOTALL)
    no_comments = re.sub(r"--.*?$", " ", no_comments, flags=re.MULTILINE)

    normalized = no_comments.strip()

    if not normalized:
        return False, "Query contains no executable SQL."

    # The query must begin with SELECT or WITH.
    first_keyword_match = re.match(r"^\s*([A-Za-z]+)", normalized)

    if not first_keyword_match:
        return False, "Could not determine the SQL statement type."

    first_keyword = first_keyword_match.group(1).upper()

    if first_keyword not in {"SELECT", "WITH"}:
        return (
            False,
            f"Only SELECT or WITH statements are allowed. Found: {first_keyword}",
        )

    # Reject explicitly forbidden operations anywhere in the query.
    # Word boundaries prevent false matches such as "updated_at".
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return False, f"Forbidden SQL operation detected: {keyword}"

    return True, "Query is valid."
