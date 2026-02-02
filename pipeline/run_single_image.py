from utils.s3_utils import load_image
from utils.compliance_parser import extract_compliance
from router.use_case_router import USE_CASE_ROUTER
from config.prompts import DEFAULT_PROMPTS

def run_single_image_pipeline(s3_uri: str, user_prompt: str | None):

    if not s3_uri.lower().endswith((".jpg", ".jpeg", ".png")):
        raise ValueError("s3_uri must point to a single image file")

    _, _, bucket, *key_parts = s3_uri.split("/")
    key = "/".join(key_parts)

    # category inferred from path
    category = key.split("/")[-2]

    if category not in USE_CASE_ROUTER:
        raise ValueError(f"Unsupported category: {category}")

    handler = USE_CASE_ROUTER[category]

    image = load_image(bucket, key)

    prompt = user_prompt or DEFAULT_PROMPTS[category]

    raw_output = handler(image, s3_uri, prompt)
    compliance = extract_compliance(raw_output)

    return {
        "s3_uri": s3_uri,
        "category": category,
        "compliance_result": compliance,
        "raw_output": raw_output
    }
