# import pandas as pd
# from utils.s3_utils import list_images, load_image
# from utils.registry import load_processed_uris
# from utils.compliance_parser import extract_compliance
# from router.use_case_router import USE_CASE_ROUTER
# from config.prompts import DEFAULT_PROMPTS

# def run_brand_pipeline(s3_uri, user_prompt, spark, processed_table):

#     _, _, bucket, *prefix = s3_uri.split("/")
#     prefix = "/".join(prefix)

#     category = prefix.rstrip("/").split("/")[-1]
#     handler = USE_CASE_ROUTER[category]

#     processed = load_processed_uris(spark, processed_table)
#     keys = list_images(bucket, prefix)

#     records = []

#     for key in keys:
#         full_uri = f"s3://{bucket}/{key}"
#         if full_uri in processed:
#             continue

#         image = load_image(bucket, key)
#         prompt = user_prompt or DEFAULT_PROMPTS[category]

#         raw = handler(image, full_uri, prompt)
#         compliance = extract_compliance(raw)

#         records.append({
#             "s3_uri": full_uri,
#             "category": category,
#             "user_prompt": prompt,
#             "compliance_output": compliance,
#             "raw_output": raw
#         })

#     return pd.DataFrame(records)


import pandas as pd
from utils.s3_utils import list_images, load_image
from utils.registry import load_processed_uris, append_to_registry
from utils.data_push import append_results
from utils.compliance_parser import extract_compliance
from router.use_case_router import USE_CASE_ROUTER
from config.prompts import DEFAULT_PROMPTS

def run_brand_pipeline(s3_uri: str, user_prompt: str | None):

    _, _, bucket, *prefix = s3_uri.split("/")
    prefix = "/".join(prefix)

    category = prefix.rstrip("/").split("/")[-1]
    handler = USE_CASE_ROUTER[category]

    processed_uris = load_processed_uris()
    image_keys = list_images(bucket, prefix)

    records = []

    for key in image_keys:
        full_uri = f"s3://{bucket}/{key}"

        if full_uri in processed_uris:
            continue

        try:
            image = load_image(bucket, key)
            prompt = user_prompt or DEFAULT_PROMPTS[category]

            raw = handler(image, full_uri, prompt)
            compliance = extract_compliance(raw)

            records.append({
                "s3_uri": full_uri,
                "category": category,
                "user_prompt": prompt,
                "compliance_output": compliance,
                "raw_output": raw
            })

        except Exception as e:
            records.append({
                "s3_uri": full_uri,
                "category": category,
                "user_prompt": user_prompt,
                "compliance_output": None,
                "raw_output": None,
                "error": str(e)
            })

    if records:
        df = pd.DataFrame(records)
        append_results(df)
        append_to_registry(records)

    return pd.DataFrame(records)
