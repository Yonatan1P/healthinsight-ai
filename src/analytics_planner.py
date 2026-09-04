import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY was not found. Check your .env file."
    )


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


PLANNER_MODEL = "minimax/minimax-m3:free"


def plan_analysis(question: str) -> dict:
    """
    Determine whether a healthcare analytics question requires
    a simple answer or a multi-part dashboard analysis.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = f"""
You are the analytics planning component of HealthInsight AI.

The application analyzes synthetic healthcare data.

Determine whether the user's question requires:

1. "simple" — a single analytical result can answer the question.
2. "dashboard" — the question asks for multiple metrics, dimensions,
   comparisons, trends, or a deeper analysis that would benefit from
   multiple visualizations or datasets.

Return ONLY valid JSON.

For a simple question, use:

{{
  "analysis_type": "simple",
  "dimensions": [],
  "metrics": []
}}

For a dashboard question, identify the dimensions and metrics needed.

Use only these available dimensions when appropriate:
- patient
- provider
- specialty
- year
- encounter_type
- diagnosis
- procedure

Use only these available metrics when appropriate:
- patient_count
- encounter_count
- readmission_count
- readmission_rate
- average_cost
- total_cost
- average_length_of_stay

Do not invent dimensions or metrics.

Do not generate SQL.

USER QUESTION:
{question}
"""

    response = client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    if getattr(response, "error", None):
        raise RuntimeError(
            f"Planner model returned an error: {response.error}"
        )

    if not response.choices:
        raise RuntimeError(
            "Planner model returned no choices."
        )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Planner model returned empty content."
        )

    content = content.strip()

    # Remove accidental markdown code fences.
    if content.startswith("```"):
        lines = content.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    try:
        plan = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Planner returned invalid JSON: {content}"
        ) from e

    if not isinstance(plan, dict):
        raise ValueError("Planner response must be a JSON object.")

    analysis_type = plan.get("analysis_type")

    if analysis_type not in {"simple", "dashboard"}:
        raise ValueError(
            "Planner returned an invalid analysis_type."
        )

    dimensions = plan.get("dimensions", [])
    metrics = plan.get("metrics", [])

    if not isinstance(dimensions, list):
        raise ValueError("Planner dimensions must be a list.")

    if not isinstance(metrics, list):
        raise ValueError("Planner metrics must be a list.")

    allowed_dimensions = {
        "patient",
        "provider",
        "specialty",
        "year",
        "encounter_type",
        "diagnosis",
        "procedure",
    }

    allowed_metrics = {
        "patient_count",
        "encounter_count",
        "readmission_count",
        "readmission_rate",
        "average_cost",
        "total_cost",
        "average_length_of_stay",
    }

    invalid_dimensions = set(dimensions) - allowed_dimensions
    invalid_metrics = set(metrics) - allowed_metrics

    if invalid_dimensions:
        raise ValueError(
            f"Planner returned invalid dimensions: {invalid_dimensions}"
        )

    if invalid_metrics:
        raise ValueError(
            f"Planner returned invalid metrics: {invalid_metrics}"
        )

    return {
        "analysis_type": analysis_type,
        "dimensions": dimensions,
        "metrics": metrics,
    }


if __name__ == "__main__":
    question = input(
        "Ask a healthcare analytics question: "
    )

    plan = plan_analysis(question)

    print("\nAnalysis plan:")
    print(json.dumps(plan, indent=2))
