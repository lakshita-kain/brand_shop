import os
import csv
from sys import excepthook
import time
import secrets
import pandas as pd
from typing import Optional
from pydantic import BaseModel
from utils.logger import logger
from fastapi import Depends, status

from fastapi import FastAPI, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from utils.data_push import push_compliance_result_to_databricks

from utils.job import job_entrypoint
from utils.data_push import append_results
import asyncio

app = FastAPI(title="Brand Shop Compliance API")
security = HTTPBasic()

API_BASIC_USER = os.getenv("API_BASIC_USER", "jk_admin")
API_BASIC_PASS = os.getenv("API_BASIC_PASS", "jk_bs!@1234")

if not API_BASIC_USER or not API_BASIC_PASS:
    raise RuntimeError("Basic Auth credentials not set")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = round(time.time() - start_time, 4)
    client_ip = request.client.host if request.client else "unknown"

    logger.info(
        f"IP={client_ip} | "
        f"METHOD={request.method} | "
        f"PATH={request.url.path} | "
        f"STATUS={response.status_code} | "
        f"DURATION={process_time}s"
    )

    return response

def verify_basic_auth(
    credentials: HTTPBasicCredentials = Depends(security)
):
    correct_username = secrets.compare_digest(
        credentials.username, API_BASIC_USER
    )
    correct_password = secrets.compare_digest(
        credentials.password, API_BASIC_PASS
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username

class ComplianceRequest(BaseModel):
    s3_uri: str
    user_prompt: Optional[str] = None

@app.post("/brand-compliance/run")
async def run_compliance(req: ComplianceRequest, user: str = Depends(verify_basic_auth)):
    try:
        loop = asyncio.get_running_loop()

        compliance_csv = "data/compliance_results.csv"
        result_row = None

        # Check if the s3_uri exists in the compliance_results.csv
        if os.path.exists(compliance_csv):
            with open(compliance_csv, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get("s3_uri") == req.s3_uri:
                        result_row = row
                        print("s3_uri already processed, fetching results:", result_row)
                        break

        if result_row is not None:
            pass  # results already assigned above
        else:
            print("s3_uri is not present")
            # Call VLM for fresh result
            result = await loop.run_in_executor(
                None,
                job_entrypoint,
                req.s3_uri,
                req.user_prompt
            )

            result_row = {
                "s3_uri": req.s3_uri,
                "user_prompt": req.user_prompt,
                **result
            }

            # --- Ensure compliance_results.csv is updated ---
            try:
                append_results(result_row)                
            except:
                print("Error in appending results to local csv")

            def safe_databricks_push():
                try:
                    push_compliance_result_to_databricks(result_row)
                except Exception as e:
                    logger.error(f"Databricks push failed: {e}")

            loop.run_in_executor(None, safe_databricks_push)

        return {
            "source": "vlm",
            "result": result_row
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Compliance pipeline failed")
        raise HTTPException(status_code=500, detail="Internal processing error")


