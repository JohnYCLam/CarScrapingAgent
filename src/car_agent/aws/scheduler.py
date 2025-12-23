from __future__ import annotations

import json
from typing import Any, Dict

from botocore.exceptions import ClientError

from car_agent.config import Settings


class Scheduler:
    def __init__(self, scheduler_client, settings: Settings):
        self._client = scheduler_client
        self._settings = settings

    def create_schedule(self, query_id: str, schedule_details: Dict[str, Any]) -> None:
        schedule_name = f"car-scraper-{query_id}"
        frequency = schedule_details["frequency"]

        try:
            self._client.create_schedule(
                Name=schedule_name,
                ScheduleExpression=frequency,
                Target={
                    "Arn": self._settings.scraper_lambda_arn,
                    "RoleArn": self._settings.scheduler_role_arn,
                    "Input": json.dumps({"query_id": query_id}),
                },
                FlexibleTimeWindow={"Mode": "OFF"},
                State="ENABLED",
            )
        except ClientError as e:
            print(f"Error creating schedule: {e}")
