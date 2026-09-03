import duckdb


DATABASE_PATH = "data/healthinsight.duckdb"


def create_database() -> None:
    """Create the HealthInsight AI DuckDB database."""

    connection = duckdb.connect(DATABASE_PATH)

    print("Creating HealthInsight AI database...")

    connection.execute("""
        CREATE OR REPLACE TABLE patients AS
        SELECT *
        FROM read_csv_auto('data/patients.csv')
    """)

    connection.execute("""
        CREATE OR REPLACE TABLE providers AS
        SELECT *
        FROM read_csv_auto('data/providers.csv')
    """)

    connection.execute("""
        CREATE OR REPLACE TABLE encounters AS
        SELECT *
        FROM read_csv_auto('data/encounters.csv')
    """)

    connection.execute("""
        CREATE OR REPLACE TABLE diagnoses AS
        SELECT *
        FROM read_csv_auto('data/diagnoses.csv')
    """)

    connection.execute("""
        CREATE OR REPLACE TABLE procedures AS
        SELECT
            procedure_id,
            encounter_id,
            CAST(procedure_code AS VARCHAR) AS procedure_code,
            procedure_name
        FROM read_csv_auto('data/procedures.csv')
    """)
    print("Database tables created successfully.")

    connection.close()


if __name__ == "__main__":
    create_database()
