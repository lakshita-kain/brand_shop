from utils.vlm_client import call_openai_vlm
from config.prompts import WORKSHOP_PROMPT

def handle(image, s3_uri: str, prompt: str | None = None):
    """
    Workshop / Service Bay compliance handler
    """
    final_prompt = prompt or WORKSHOP_PROMPT
    return call_openai_vlm(image, final_prompt)
