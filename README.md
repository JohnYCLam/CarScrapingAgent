# Car Scraping Agent (Drive.com.au) + LLM + AWS

A modular, AI-powered prototype agent designed to crawl, extract, and process used car sales information. This project serves as a comprehensive demonstration of **end-to-end cloud deployment**, moving from local Python scripts to a fully serverless architecture on AWS. The idea originates from building an AI agent to assist me to consolidate used car sales information.


## Project structure
```
car-scraping-agent/

├─ environment.yml
├─ README.md
├─ src/
│ └─ car_agent/
│ ├─ agent.py
│ ├─ config.py
│ ├─ schemas.py
│ ├─ aws/
│ ├─ llm/
│ └─ scraping/
└─ scripts/
```

## The Mission
Finding the perfect used car deal manually is time-consuming. This agent automates the search by:

Scraping raw HTML from automotive marketplaces.

Processing unstructured data into clean JSON using LangChain and LLMs.

Storing results in the cloud and notifying the user of new finds.

## Tech Stack & Tools
**Artificial Intelligence**

**LangChain**: Orchestrates the workflow and handles prompt engineering.

**LLMs (OpenAI/Anthropic)**: Used to "read" the webpage and extract car specs (Price, Mileage, Year, Condition).

**Cloud Infrastructure (AWS)**

**AWS Lambda**: Serverless execution of scraping tasks.

**AWS S3**: Persistent storage for raw HTML snapshots and processed JSON data.

**AWS SES**: Automated email alerts when a target car is found.

**AWS IAM**: Fine-grained security and permissions management.

**Engineering Excellence**

**Pydantic**: Strict data validation via schemas.py.

**Conda**: Reproducible environment management via environment.yml.

**Scripts**: Unit testing suite for scraping logic and data integrity.

## Prerequisites

- Conda (Anaconda / Miniconda / Miniforge)
- Docker Desktop (for DynamoDB Local)
- An OpenAI API key set as `OPENAI_API_KEY`

### Why Docker is used here
Docker is only needed to run **DynamoDB Local** for local testing (so you don’t hit AWS while developing). DynamoDB Local is typically exposed at `http://localhost:8000`. [web:244][web:379]

## Setup (local development)

### 1) Create the Conda environment

From the project root (where `environment.yml` lives):
```
conda env create -f environment.yml
conda activate car-scraper
```
Conda reads dependencies from the YAML file and creates the environment. [web:317][web:318]

### 2) Configure environment variables

Create a `.env` file (or set environment variables in your shell):

Required for LLM calls
OPENAI_API_KEY=...

If you want AWS calls locally (SES/Scheduler), configure AWS creds too (optional)
AWS_REGION=us-east-1

DynamoDB tables (optional overrides)
CAR_QUERIES_TABLE=CarQueries
CAR_RESULTS_TABLE=CarSearchResults

For SES (optional)
FROM_EMAIL=you@yourdomain.com

For EventBridge Scheduler targeting a Lambda (optional)
SCRAPER_LAMBDA_ARN=arn:aws:lambda:...
SCHEDULER_ROLE_ARN=arn:aws:iam::...:role/...

> Tip: For local-only runs without AWS, you can still test scraping + LLM parsing with just `OPENAI_API_KEY`.

## Run DynamoDB Local (Docker)

### First time only: pull the image
docker pull amazon/dynamodb-local

You only need to pull again if you want to update the image. (Docker caches it locally.)  

### Start DynamoDB Local (background)
docker run -d --name dynamodb-local -p 8000:8000 amazon/dynamodb-local

Verify it’s running:
docker ps

Stop it when done:
docker stop dynamodb-local

## Local testing

### 1) Quick scrape test

Create `scripts/test_scrape.py` (or run in a notebook):

from car_agent.config import Settings
from car_agent.llm.client import build_llm
from car_agent.scraping.drive_scraper import scrape_drive

settings = Settings()
llm = build_llm(settings)

criteria = {"make": "Mazda", "model": "CX-3", "year_min": 2015, "price_max": 20000}
results = scrape_drive(criteria, llm=llm, max_results=30, max_page=2)

print("count:", len(results))
print(results[:3])

Run it:
python scripts/test_scrape.py

### 2) DynamoDB Local test (boto3 endpoint)

Create `scripts/test_dynamodb_local.py`:

import boto3

dynamodb = boto3.resource(
"dynamodb",
endpoint_url="http://localhost:8000",
region_name="us-east-1",
aws_access_key_id="fake",
aws_secret_access_key="fake",
)

print("Connected to DynamoDB Local")
print([t.name for t in dynamodb.tables.all()])

This uses `endpoint_url="http://localhost:8000"` to target DynamoDB Local. [web:244][web:379]

## AWS deployment (high level)

When you deploy to AWS Lambda:
- Put your handler in a dedicated file (e.g., `car_agent/lambda_handler.py`) with:
def lambda_handler(event, context):
...

Lambda calls a handler function with `(event, context)`. [web:363]
- You can deploy as:
- ZIP (simpler for small deps), or
- Container image (more control over native deps).

This repo is structured so code is modular and testable before deployment.

## Notes / gotchas

- Drive.com.au filtering is partly URL-hash based; scraping with `requests` may not match browser behavior exactly, so this project also applies post-filters after parsing.
- Be polite with request rates (sleep between pages) to reduce blocking risk.
- If you see 403s, reduce scraping frequency, try fewer pages, or switch to a headless browser approach.

## License

Personal project / educational use.






