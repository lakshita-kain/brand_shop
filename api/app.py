import time
from utils.logger import logger
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from utils.data_push import push_compliance_result_to_databricks

from utils.job import job_entrypoint
import asyncio

app = FastAPI(title="Brand Shop Compliance API")

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

class ComplianceRequest(BaseModel):
    s3_uri: str
    user_prompt: Optional[str] = None

@app.post("/brand-compliance/run")
async def run_compliance(req: ComplianceRequest):
    try:
        # Run sync code in threadpool for async API
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            job_entrypoint,
            req.s3_uri,
            req.user_prompt
        )

         # Databricks push
        loop.run_in_executor(
            None,
            push_compliance_result_to_databricks,
            {
                "s3_uri": req.s3_uri,
                "user_prompt": req.user_prompt,
                **result
            }
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal processing error")




