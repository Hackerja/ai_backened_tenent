from google import genai
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask(data, query):
    context = "\n\n".join(item["content"] for item in data)  # is a string

    prompt = f"""You are a strict, analytical answering agent. Your only purpose is to answer the user's query based EXCLUSIVELY on the information provided in the <context> block below.

    RULES:
    1. Do not use outside knowledge, prior training data, or assumptions to answer the question.
    2. If the answer cannot be explicitly found in the <context> block, you must output EXACTLY: "I cannot answer this based on the provided documents."
    3. Do not attempt to guess, extrapolate, or invent information.
    4. Keep your answer direct and cite the specific part of the context used.

    <context>
    {context}
    </context>

    [USER]
    {query}"""

    response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

    return response.text
    