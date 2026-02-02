import base64
from io import BytesIO
from openai import OpenAI
from config.setting import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

JSON_APPENDIX = """
IMPORTANT:
Return JSON ONLY.
The response MUST be a single valid JSON object.
Do NOT use markdown, code blocks, or extra text.
The JSON MUST include the key "branding" with value exactly:
- "pass"
- "fail"
"""

def call_openai_vlm(image, prompt):
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    final_prompt = f"{prompt}\n\n{JSON_APPENDIX}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON-only compliance auditor. "
                    "Return exactly one JSON object and nothing else."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": final_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
