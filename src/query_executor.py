import duckdb

from src.sql_validator import validate_sql

DATABASE_PATH = "data/healthinsight.duckdb"


def execute_query(sql: str):
    """
    Validate and execute a read-only SQL query.

    Returns:
        Query results as a Pandas DataFrame.
    """

    # Validate the SQL before executing it
    is_valid, message = validate_sql(sql)

    if not is_valid:
        raise ValueError(message)

    # Connect to the healthcare database
    connection = duckdb.connect(DATABASE_PATH)

    try:
        # Execute the validated query
        result = connection.execute(sql).fetchdf()
    finally:
        # Always close the database connection
        connection.close()

    return result
