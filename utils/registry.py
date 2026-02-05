# def load_processed_uris(spark, table_name):
#     try:
#         df = spark.table(table_name).select("s3_uri").distinct()
#         return set(row.s3_uri for row in df.collect())
#     except Exception:
#         return set()


import os
import pandas as pd
from datetime import datetime

REGISTRY_PATH = "data/processed_registry.csv"
COMPLIANCE_CSV = "/data/compliance_results.csv"

# def load_processed_uris() -> set:
#     if not os.path.exists(REGISTRY_PATH):
#         return set()

#     df = pd.read_csv(REGISTRY_PATH)
#     return set(df["s3_uri"].unique())


def append_to_registry(records: list[dict]):
    """
    records must contain: s3_uri, category
    """
    os.makedirs("data", exist_ok=True)

    new_df = pd.DataFrame([
        {
            "s3_uri": r["s3_uri"],
            "category": r["category"],
            "processed_at": datetime.utcnow().isoformat()
        }
        for r in records
    ])

    if os.path.exists(REGISTRY_PATH):
        existing = pd.read_csv(REGISTRY_PATH)
        new_df = pd.concat([existing, new_df], ignore_index=True)

    new_df.to_csv(REGISTRY_PATH, index=False)

def get_compliance_by_s3_uri(s3_uri: str):
    """
    Fetch existing compliance result for given s3_uri if present.
    Returns full row as dict or None.
    """
    if not os.path.exists(COMPLIANCE_CSV):
        return None

    df = pd.read_csv(COMPLIANCE_CSV)

    if "s3_uri" not in df.columns:
        return None

    match = df[df["s3_uri"] == s3_uri]

    if match.empty:
        return None

    return match.iloc[0].to_dict()
