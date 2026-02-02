import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AWS_ACCESS_KEY = os.getenv("AWS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

DEFAULT_BUCKET = "algo-8-beat-optimization"

PROCESSED_TABLE = "brand_shop.compliance_results"