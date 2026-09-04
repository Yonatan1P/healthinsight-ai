from src.sql_agent import generate_sql
from src.query_executor import execute_query
from src.explainer import explain_results

def ask(question: str):
    """
    Run a natural-language healthcare analytics question
    through SQL generation and database execution.
    """

    # Generate SQL from the user's question
    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)

    # Execute the generated SQL
    results = execute_query(sql)

    # Explain the results in plain language
    explanation = explain_results(question, sql, results)

    print("\nExplanation:")
    print(explanation)

    return results
