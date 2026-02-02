# from pyspark.sql import SparkSession
# from pipeline.run_pipeline import run_brand_pipeline
# from config.setting import PROCESSED_TABLE

# def job_entrypoint(s3_uri, user_prompt=None):
#     spark = SparkSession.builder.appName("DataPushJob").getOrCreate()

#     df = run_brand_pipeline(
#         s3_uri=s3_uri,
#         user_prompt=user_prompt,
#         spark=spark,
#         processed_table=PROCESSED_TABLE
#     )

#     spark.createDataFrame(df).write.mode("append").saveAsTable(PROCESSED_TABLE)


import os
import pandas as pd

OUTPUT_PATH = "data/compliance_results.csv"

def append_results(df: pd.DataFrame):
    os.makedirs("data", exist_ok=True)

    if os.path.exists(OUTPUT_PATH):
        existing = pd.read_csv(OUTPUT_PATH)
        df = pd.concat([existing, df], ignore_index=True)

    df.to_csv(OUTPUT_PATH, index=False)



