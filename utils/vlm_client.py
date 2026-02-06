import httpx
import base64
import asyncio
from io import BytesIO
from typing import Any, Dict
from config.setting import OPENAI_API_KEY

JSON_APPENDIX = """
STRICT RULES:
- Describe ONLY what is directly visible in the image.
- Do NOT infer intent, ownership, or context beyond the image.
- If something is not clearly visible, mark it as "uncertain".
- Do NOT add explanations, reasoning steps, or recommendations.
- Do NOT include any text outside the JSON response.

FINAL OUTPUT REQUIREMENTS:
- Return exactly ONE valid JSON object.
- Do NOT use markdown, code blocks, or additional text.
- All values must be lowercase strings.

The JSON object MUST contain the following keys:
- branding: "pass" or "fail"
- notes: brief, factual visual observations only
- jk_branding_presence: "present", "absent", or "uncertain"
- competing_brand_presence: "none", "present", or "uncertain"
- logo_correctness: "correct", "incorrect", or "uncertain"

DEFINITION OF PASS / FAIL:
- "pass" → JK Tyre branding is clearly present, logo appears correct, and no competing brands are visible.
- "fail" → JK Tyre branding is absent, incorrect, unclear, or competing brands are visible."""

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
                    "You are an expert brand compliance auditor for JK Tyre."
                    "Your task is to analyze the provided image of a dealer’s brandshop and assess JK Tyre brand compliance."
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
