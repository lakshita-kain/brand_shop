import base64
import asyncio
from io import BytesIO
from typing import Any, Dict

import httpx

from config.setting import OPENAI_API_KEY

JSON_APPENDIX = """
IMPORTANT:
Return JSON ONLY.
The response MUST be a single valid JSON object.
Do NOT use markdown, code blocks, or extra text.
The JSON MUST include the key "branding" with value exactly:
- "pass"
- "fail"
"""

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"


async def _call_openai_vlm_async(image, prompt: str) -> str:
    """
    Async VLM call using httpx to OpenAI's chat completions endpoint.
    """
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    final_prompt = f"{prompt}\n\n{JSON_APPENDIX}"

    payload: Dict[str, Any] = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict JSON-only compliance auditor. "
                    "Return exactly one JSON object and nothing else."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                        },
                    },
                ],
            },
        ],
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(OPENAI_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]


def call_openai_vlm(image, prompt: str) -> str:
    """
    Synchronous wrapper around the async httpx-based VLM call.

    This keeps the rest of the pipeline/handlers API unchanged, while
    actually performing the network call asynchronously with httpx.
    """
    return asyncio.run(_call_openai_vlm_async(image, prompt))
