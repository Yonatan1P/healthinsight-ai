import duckdb


DATABASE_PATH = "data/healthinsight.duckdb"


def validate_database() -> None:
    """Validate the HealthInsight AI database relationships."""

    connection = duckdb.connect(DATABASE_PATH)

    print("Validating HealthInsight AI database...")
    print()

    tables = connection.execute("SHOW TABLES").fetchdf()["name"].tolist()

    expected_tables = {
        "patients",
        "providers",
        "encounters",
        "diagnoses",
        "procedures",
    }

    if set(tables) != expected_tables:
        raise ValueError(
            f"Unexpected tables. Found: {tables}"
        )

    print("✓ All expected tables exist")

    invalid_patients = connection.execute("""
        SELECT COUNT(*)
        FROM encounters e
        LEFT JOIN patients p
            ON e.patient_id = p.patient_id
        WHERE p.patient_id IS NULL
    """).fetchone()[0]

    if invalid_patients != 0:
        raise ValueError(
            f"Found {invalid_patients} encounters with invalid patient IDs"
        )

    print("✓ All encounters reference valid patients")

    invalid_providers = connection.execute("""
        SELECT COUNT(*)
        FROM encounters e
        LEFT JOIN providers p
            ON e.provider_id = p.provider_id
        WHERE p.provider_id IS NULL
    """).fetchone()[0]

    if invalid_providers != 0:
        raise ValueError(
            f"Found {invalid_providers} encounters with invalid provider IDs"
        )

    print("✓ All encounters reference valid providers")

    invalid_diagnoses = connection.execute("""
        SELECT COUNT(*)
        FROM diagnoses d
        LEFT JOIN encounters e
            ON d.encounter_id = e.encounter_id
        WHERE e.encounter_id IS NULL
    """).fetchone()[0]

    if invalid_diagnoses != 0:
        raise ValueError(
            f"Found {invalid_diagnoses} diagnoses with invalid encounter IDs"
        )

    print("✓ All diagnoses reference valid encounters")

    invalid_procedures = connection.execute("""
        SELECT COUNT(*)
        FROM procedures p
        LEFT JOIN encounters e
            ON p.encounter_id = e.encounter_id
        WHERE e.encounter_id IS NULL
    """).fetchone()[0]

    if invalid_procedures != 0:
        raise ValueError(
            f"Found {invalid_procedures} procedures with invalid encounter IDs"
        )

    print("✓ All procedures reference valid encounters")

    print()
    print("Database validation passed.")

    connection.close()


if __name__ == "__main__":
    validate_database()
