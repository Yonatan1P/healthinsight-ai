from src.analytics_planner import plan_analysis
from src.sql_agent import generate_sql
from src.query_executor import execute_query
from src.explainer import explain_results
from src.dashboard_queries import build_provider_year_analysis


def ask(question: str):
    """
    Run a natural-language healthcare analytics question.

    Simple questions use the existing single-query pipeline.
    Dashboard questions use the multi-dataset dashboard pipeline.
    """

    plan = plan_analysis(question)

    # ----------------------------------------
    # Dashboard analysis
    # ----------------------------------------

    if plan["analysis_type"] == "dashboard":

        datasets = build_provider_year_analysis()

        return {
            "question": question,
            "analysis_type": "dashboard",
            "plan": plan,
            "datasets": datasets,
        }

    # ----------------------------------------
    # Simple analysis
    # ----------------------------------------

    sql = generate_sql(question)
    results = execute_query(sql)
    explanation = explain_results(
        question,
        sql,
        results,
    )

    return {
        "question": question,
        "analysis_type": "simple",
        "plan": plan,
        "sql": sql,
        "results": results,
        "explanation": explanation,
    }
