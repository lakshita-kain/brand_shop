import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from typing import Dict, List, Union
from utils.dlt_utils import DLTWriter   

OUTPUT_PATH = "data/compliance_results.csv"

def append_results(data: Union[pd.DataFrame, Dict, List[Dict]]):
    """
    Append new compliance results to the CSV, accepting either
    DataFrames or dict payloads from the API.
    """
    os.makedirs("data", exist_ok=True)

    # Normalize to DataFrame
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame([data])

    if os.path.exists(OUTPUT_PATH):
        existing = pd.read_csv(OUTPUT_PATH)
        df = pd.concat([existing, df], ignore_index=True)

    df.to_csv(OUTPUT_PATH, index=False)


def push_compliance_result_to_databricks(
    data: Union[Dict, List[Dict]],
    table_name: str = "brand_compliance_results",
    mode: str = "append"
) -> bool:
    """
    Push compliance results to Databricks using DLTWriter.

    Args:
        data: dict or list of dicts (API output)
        table_name: target Delta table
        mode: append / overwrite

    Returns:
        bool: success flag
    """
    try:
        # Normalize data → list[dict]
        if isinstance(data, dict):
            data = [data]

        # Convert to Pandas
        df = pd.DataFrame(data)

        # Add ingestion metadata (VERY useful)
        df["ingested_at"] = datetime.utcnow()
        df["source"] = "brand_shop_api"

        # Initialize writer
        writer = DLTWriter(
            catalog="provisioned-tableau-data",
            schema="data_science"
        )

        # Write to Databricks
        success = writer.write_table(
            df=df,
            table_name=table_name,
            mode=mode,
            merge_schema=True
        )

        return success

    except Exception as e:
        print(f"❌ Failed to push data to Databricks: {e}")
        return False

