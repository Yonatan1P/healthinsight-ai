import duckdb
import pandas as pd

DATABASE_PATH = "data/healthinsight.duckdb"


def execute_dashboard_query(sql: str, params=None) -> pd.DataFrame:
    connection = duckdb.connect(DATABASE_PATH)
    try:
        if params:
            return connection.execute(sql, params).fetchdf()
        return connection.execute(sql).fetchdf()
    finally:
        connection.close()


def build_provider_year_analysis(filters=None) -> dict[str, pd.DataFrame]:
    filters = filters or {}

    where_clauses = []
    params = []

    if filters.get("year") is not None:
        where_clauses.append("EXTRACT(YEAR FROM e.encounter_date) = ?")
        params.append(filters["year"])

    if filters.get("provider_id") is not None:
        where_clauses.append("e.provider_id = ?")
        params.append(filters["provider_id"])

    if filters.get("specialty") is not None:
        where_clauses.append("p.specialty = ?")
        params.append(filters["specialty"])

    if filters.get("encounter_type") is not None:
        where_clauses.append("e.encounter_type = ?")
        params.append(filters["encounter_type"])

    where_sql = ""

    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    datasets = {}

    datasets["kpis"] = execute_dashboard_query(
        f"""
        SELECT
            COUNT(DISTINCT e.patient_id) AS patient_count,
            COUNT(*) AS encounter_count,
            SUM(
                CASE
                    WHEN e.readmitted_30_days = TRUE THEN 1
                    ELSE 0
                END
            ) AS readmission_count,
            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN e.readmitted_30_days = TRUE THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS readmission_rate,
            ROUND(AVG(e.total_cost), 2) AS average_cost,
            ROUND(SUM(e.total_cost), 2) AS total_cost
        FROM encounters e
        JOIN providers p
            ON e.provider_id = p.provider_id
        {where_sql}
        """,
        params,
    )

    datasets["patient_volume"] = execute_dashboard_query(
        f"""
        SELECT
            EXTRACT(YEAR FROM e.encounter_date) AS year,
            e.provider_id,
            p.provider_name,
            p.specialty,
            COUNT(DISTINCT e.patient_id) AS patient_count
        FROM encounters e
        JOIN providers p
            ON e.provider_id = p.provider_id
        {where_sql}
        GROUP BY
            year,
            e.provider_id,
            p.provider_name,
            p.specialty
        ORDER BY year, patient_count DESC
        """,
        params,
    )

    datasets["readmissions"] = execute_dashboard_query(
        f"""
        SELECT
            EXTRACT(YEAR FROM e.encounter_date) AS year,
            e.provider_id,
            p.provider_name,
            p.specialty,
            SUM(
                CASE
                    WHEN e.readmitted_30_days = TRUE THEN 1
                    ELSE 0
                END
            ) AS readmission_count,
            COUNT(*) AS encounter_count,
            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN e.readmitted_30_days = TRUE THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS readmission_rate
        FROM encounters e
        JOIN providers p
            ON e.provider_id = p.provider_id
        {where_sql}
        GROUP BY
            year,
            e.provider_id,
            p.provider_name,
            p.specialty
        ORDER BY year, readmission_rate DESC
        """,
        params,
    )

    datasets["encounter_mix"] = execute_dashboard_query(
        f"""
        SELECT
            e.encounter_type,
            COUNT(*) AS encounter_count
        FROM encounters e
        JOIN providers p
            ON e.provider_id = p.provider_id
        {where_sql}
        GROUP BY e.encounter_type
        ORDER BY encounter_count DESC
        """,
        params,
    )

    datasets["provider_detail"] = execute_dashboard_query(
        f"""
        SELECT
            e.provider_id,
            p.provider_name,
            p.specialty,
            COUNT(DISTINCT e.patient_id) AS patient_count,
            COUNT(*) AS encounter_count,
            SUM(
                CASE
                    WHEN e.readmitted_30_days = TRUE THEN 1
                    ELSE 0
                END
            ) AS readmission_count,
            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN e.readmitted_30_days = TRUE THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS readmission_rate,
            ROUND(AVG(e.total_cost), 2) AS average_cost,
            ROUND(SUM(e.total_cost), 2) AS total_cost
        FROM encounters e
        JOIN providers p
            ON e.provider_id = p.provider_id
        {where_sql}
        GROUP BY
            e.provider_id,
            p.provider_name,
            p.specialty
        ORDER BY patient_count DESC
        """,
        params,
    )

    return datasets


if __name__ == "__main__":
    data = build_provider_year_analysis()

    for name, dataframe in data.items():
        print(f"\n{'=' * 60}")
        print(name)
        print(f"{'=' * 60}")
        print(dataframe.head(10).to_string(index=False))
