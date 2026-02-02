# from pipeline.run_pipeline import run_brand_pipeline

# def job_entrypoint(s3_uri, user_prompt=None):
#     df = run_brand_pipeline(s3_uri, user_prompt)
#     return {
#         "processed": len(df)
#     }

from pipeline.run_single_image import run_single_image_pipeline

def job_entrypoint(s3_uri, user_prompt=None):
    return run_single_image_pipeline(
        s3_uri=s3_uri,
        user_prompt=user_prompt
    )
