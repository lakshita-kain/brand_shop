from utils.vlm_client import call_openai_vlm
from config.prompts import BRAND_WALL_PROMPT

def handle(image, s3_uri: str, prompt: str | None = None):
    """
    Brand Wall quality compliance handler
    """
    final_prompt = prompt or BRAND_WALL_PROMPT
    return call_openai_vlm(image, final_prompt)
