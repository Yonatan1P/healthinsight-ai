import duckdb


DATABASE_PATH = "data/healthinsight.duckdb"


RELATIONSHIPS = [
    {
        "from_table": "encounters",
        "from_column": "patient_id",
        "to_table": "patients",
        "to_column": "patient_id",
    },
    {
        "from_table": "encounters",
        "from_column": "provider_id",
        "to_table": "providers",
        "to_column": "provider_id",
    },
    {
        "from_table": "diagnoses",
        "from_column": "encounter_id",
        "to_table": "encounters",
        "to_column": "encounter_id",
    },
    {
        "from_table": "procedures",
        "from_column": "encounter_id",
        "to_table": "encounters",
        "to_column": "encounter_id",
    },
]


def get_schema() -> dict[str, list[str]]:
    """Return the database schema as a dictionary."""

    connection = duckdb.connect(DATABASE_PATH)

    tables = connection.execute(
        "SHOW TABLES"
    ).fetchdf()["name"].tolist()

    schema = {}

    for table in tables:
        columns = connection.execute(
            f"DESCRIBE {table}"
        ).fetchdf()

        schema[table] = columns["column_name"].tolist()

    connection.close()

    return schema


def get_relationships() -> list[dict[str, str]]:
    """Return relationships between healthcare tables."""

    return RELATIONSHIPS


if __name__ == "__main__":
    schema = get_schema()
    relationships = get_relationships()

    print("DATABASE SCHEMA")

    for table, columns in schema.items():
        print(f"\n{table}:")
        for column in columns:
            print(f"  - {column}")

    print("\nRELATIONSHIPS")

    for relationship in relationships:
        print(
            f"  {relationship['from_table']}."
            f"{relationship['from_column']}"
            f" -> "
            f"{relationship['to_table']}."
            f"{relationship['to_column']}"
        )
