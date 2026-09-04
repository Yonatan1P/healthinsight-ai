import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from src.agent_context import build_schema_context


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


PRIMARY_MODEL = "minimax/minimax-m3:free"
FALLBACK_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


def clean_sql(text: str) -> str:
    """
    Clean SQL returned by the LLM.

    Removes markdown code fences and surrounding whitespace.
    """

    if not text:
        raise ValueError("The SQL model returned an empty response.")

    sql = text.strip()

    sql = re.sub(
        r"^```(?:sql)?\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
    )

    sql = sql.strip()

    if not sql:
        raise ValueError("The SQL model returned an empty SQL query.")

    return sql


def _generate_with_model(model: str, prompt: str) -> str:
    """
    Generate SQL using a specific model.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    if getattr(response, "error", None):
        error = response.error

        if isinstance(error, dict):
            message = error.get("message", "Unknown model error.")
            code = error.get("code")

            if code:
                raise RuntimeError(
                    f"{model} returned an error ({code}): {message}"
                )

            raise RuntimeError(
                f"{model} returned an error: {message}"
            )

        raise RuntimeError(
            f"{model} returned an error: {error}"
        )

    if not response.choices:
        raise RuntimeError(
            f"{model} returned no choices."
        )

    content = response.choices[0].message.content

    if content is None:
        raise RuntimeError(
            f"{model} returned no SQL content."
        )

    return clean_sql(content)


def generate_sql(question: str) -> str:
    """
    Convert a natural-language healthcare question into SQL.

    Uses MiniMax M3 as the primary model and Nemotron as a fallback
    if the primary model fails.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    schema_context = build_schema_context()

    prompt = f"""
You are a SQL analyst working with a synthetic healthcare database.

{schema_context}

Convert the user's question into a DuckDB SQL query.

Rules:
- Return ONLY the SQL query.
- Do not use markdown code fences.
- Do not explain the query.
- Do not include reasoning.
- Use only tables and columns provided in the database schema.
- The query must be read-only.
- Only SELECT or WITH statements are allowed.
- Do not modify the database.

User question:
{question}
"""

    try:
        return _generate_with_model(
            PRIMARY_MODEL,
            prompt,
        )

    except Exception as primary_error:
        print(
            f"Primary SQL model failed: {primary_error}"
        )

        try:
            return _generate_with_model(
                FALLBACK_MODEL,
                prompt,
            )

        except Exception as fallback_error:
            raise RuntimeError(
                "Both SQL generation models failed.\n"
                f"Primary model: {primary_error}\n"
                f"Fallback model: {fallback_error}"
            ) from fallback_error


if __name__ == "__main__":
    question = input(
        "Ask a healthcare analytics question: "
    )

    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)
