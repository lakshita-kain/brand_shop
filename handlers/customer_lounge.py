from utils.vlm_client import call_openai_vlm
from config.prompts import CUSTOMER_LOUNGE_PROMPT

def handle(image, s3_uri: str, prompt: str | None = None):
    """
    Customer Lounge compliance handler
    """
    final_prompt = prompt or CUSTOMER_LOUNGE_PROMPT
    return call_openai_vlm(image, final_prompt)
