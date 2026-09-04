from src.schema import get_relationships, get_schema


def build_schema_context() -> str:
    """Build a text representation of the database for the AI agent."""

    schema = get_schema()
    relationships = get_relationships()

    lines = [
        "You are querying a synthetic healthcare analytics database.",
        "",
        "DATABASE TABLES:",
    ]

    for table, columns in schema.items():
        lines.append(f"\nTable: {table}")

        for column in columns:
            lines.append(f"  - {column}")

    lines.append("")
    lines.append("TABLE RELATIONSHIPS:")

    for relationship in relationships:
        lines.append(
            f"  - {relationship['from_table']}."
            f"{relationship['from_column']}"
            f" joins to "
            f"{relationship['to_table']}."
            f"{relationship['to_column']}"
        )

    lines.append("")
    lines.append("IMPORTANT RULES:")
    lines.append("  - Generate read-only SQL queries.")
    lines.append("  - Only SELECT statements are allowed.")
    lines.append("  - Do not modify the database.")
    lines.append("  - This database contains synthetic healthcare data.")
    lines.append("  - Do not provide medical diagnosis or treatment advice.")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_schema_context())
