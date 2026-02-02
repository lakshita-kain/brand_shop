from utils.vlm_client import call_openai_vlm
from config.prompts import MAIN_SIGNAGE_PROMPT

def handle(image, s3_uri: str, prompt: str | None = None):
    """
    Main Signage quality compliance handler
    """
    final_prompt = prompt or MAIN_SIGNAGE_PROMPT
    return call_openai_vlm(image, final_prompt)
