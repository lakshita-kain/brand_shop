from utils.vlm_client import call_openai_vlm
from config.prompts import TYRE_DISPLAY_PROMPT

def handle(image, s3_uri: str, prompt: str | None = None):
    """
    Tyre Display Area compliance handler
    """
    final_prompt = prompt or TYRE_DISPLAY_PROMPT
    return call_openai_vlm(image, final_prompt)
