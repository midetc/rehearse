import os
import json
from groq import Groq


def draft_card(topic: str) -> dict:
    if not topic:
        raise ValueError("Topic cannot be empty")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if GROQ_API_KEY is None:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    instruction = (
        "Generate exactly one job interview question and a short, clear answer in "
        "English. Return only a valid JSON object with exactly two keys: "
        "'question' and 'answer'. Do not include any explanations, Markdown, or "
        f"additional text. Draft a card for the topic: {topic}"
    )

    client = Groq()
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": topic},
        ],
        response_format={"type": "json_object"},
    )
    text = completion.choices[0].message.content
    json_object = json.loads(text)
    return json_object