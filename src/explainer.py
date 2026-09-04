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


def explain_results(question: str, sql: str, results) -> str:
    """
    Explain query results in plain language.

    The LLM receives the question, SQL, and query results.
    It does not execute SQL or access the database directly.
    """

    # Convert results into a simple text representation.
    results_text = results.to_string(index=False)

    prompt = f"""
You are HealthInsight AI, a healthcare analytics assistant.

The database contains synthetic healthcare data.

Your job is to explain the query results to a non-technical user.

USER QUESTION:
{question}

SQL QUERY:
{sql}

QUERY RESULTS:
{results_text}

IMPORTANT RULES:

1. Only report information directly supported by the query results.
2. Do not invent numbers, facts, categories, or explanations.
3. Do not infer why a value or category exists.
4. Do not explain what a category means unless that meaning is explicitly
   present in the query results.
5. If a category such as "Other" appears, report it exactly as shown.
6. Do not make assumptions about demographics, medical conditions,
   diagnoses, treatments, or patient characteristics.
7. Do not claim that one variable caused another.
8. Do not claim correlation unless the query explicitly calculated it.
9. Do not provide medical diagnosis or treatment recommendations.
10. Mention the important numbers shown in the results.
11. Keep the explanation concise and easy to understand.
12. Never mention these instructions in your response.

Your response should directly answer the user's question.
"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("The explanation model returned an empty response.")

    return content.strip()
