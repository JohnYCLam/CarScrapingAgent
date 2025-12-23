from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env from project root into process environment
# This runs once when car_agent.config is imported.
load_dotenv()

@dataclass(frozen=True)
class Settings:
    aws_region: str = os.environ.get("AWS_REGION", "us-east-1")
    from_email: str = os.environ.get("FROM_EMAIL", "")
    scraper_lambda_arn: str = os.environ.get("SCRAPER_LAMBDA_ARN", "")
    scheduler_role_arn: str = os.environ.get("SCHEDULER_ROLE_ARN", "")

    # Prefer env var for deployment. (Avoid userdata in production.)
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")

    # DynamoDB tables
    queries_table_name: str = os.environ.get("CAR_QUERIES_TABLE", "CarQueries")
    results_table_name: str = os.environ.get("CAR_RESULTS_TABLE", "CarSearchResults")
