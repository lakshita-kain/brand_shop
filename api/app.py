from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from utils.job import job_entrypoint

import asyncio

app = FastAPI(title="Brand Shop Compliance API")

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
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal processing error")
