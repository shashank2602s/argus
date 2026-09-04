import json
import os

import anthropic
from dotenv import load_dotenv


load_dotenv()


class ReasoningError(Exception):
    """Raised when the reasoning model cannot produce a valid response."""


def ask_for_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Send a prompt to Claude and return the response as a JSON object.
    """

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ReasoningError(
            "ANTHROPIC_API_KEY is not set. Add it to the .env file."
        )

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )
    except anthropic.AuthenticationError as exc:
        raise ReasoningError(
            "Anthropic API authentication failed. Check your API key."
        ) from exc
    except anthropic.RateLimitError as exc:
        raise ReasoningError(
            "Anthropic API rate limit exceeded. Try again later."
        ) from exc
    except anthropic.APIError as exc:
        raise ReasoningError(
            f"Anthropic API error: {exc}"
        ) from exc

    if not response.content:
        raise ReasoningError("Anthropic returned an empty response.")

    text = response.content[0].text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ReasoningError(
            f"Anthropic returned invalid JSON: {text}"
        ) from exc