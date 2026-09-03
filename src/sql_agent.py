import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from agent_context import build_schema_context

# Load variables from the .env file
load_dotenv()

# Get the OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")

# Stop the program if the key is missing
if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY was not found. Check your .env file."
    )

# Create a client connected to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def generate_sql(question: str) -> str:
    """
    Convert a natural-language healthcare question into SQL.
    """
    schema_context = build_schema_context()
    prompt = f"""
You are a SQL analyst working with a synthetic healthcare database.

{schema_context}

Convert the user's question into a DuckDB SQL query.

Rules:
- Return ONLY the SQL query.
- Do not use markdown code fences.
- Use only tables and columns provided in the database schema.
- The query must be read-only.
- Only SELECT statements are allowed.

User question:
{question}
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

if __name__ == "__main__":
    question = input("Ask a healthcare analytics question: ")
    sql = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql)
