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

    The LLM receives the question, SQL, and results,
    but does not execute any SQL.
    """

    prompt = f"""
You are a healthcare analytics assistant.

The database contains synthetic healthcare data.

User question:
{question}

SQL query used:
{sql}

Query results:
{results.to_string(index=False)}

Explain the results clearly and concisely for a non-technical user.

Rules:
- Only describe what the data shows.
- Do not claim that one variable caused another.
- Do not provide medical diagnosis or treatment recommendations.
- Do not invent information that is not present in the results.
- Mention important numbers from the results.
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

    return response.choices[0].message.content.strip()
