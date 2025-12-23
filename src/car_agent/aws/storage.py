from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from botocore.exceptions import ClientError

from car_agent.config import Settings


class Storage:
    def __init__(self, dynamodb_resource, settings: Settings):
        self._settings = settings
        self.queries_table = dynamodb_resource.Table(settings.queries_table_name)
        self.results_table = dynamodb_resource.Table(settings.results_table_name)

    def store_search(self, user_id: str, criteria: Dict[str, Any], results: List[Dict[str, Any]], query_type: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        try:
            self.results_table.put_item(Item={
                "user_id": user_id,
                "timestamp": timestamp,
                "criteria": json.dumps(criteria),
                "results": json.dumps(results),
                "query_type": query_type,
                "result_count": len(results),
            })
        except ClientError as e:
            print(f"Error storing search: {e}")

    def store_recurring_query(self, user_id: str, criteria: Dict[str, Any], schedule_details: Dict[str, Any]) -> Optional[str]:
        query_id = f"{user_id}_{int(datetime.utcnow().timestamp())}"
        timestamp = datetime.utcnow().isoformat()

        try:
            self.queries_table.put_item(Item={
                "query_id": query_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "criteria": json.dumps(criteria),
                "email": schedule_details["email"],
                "frequency": schedule_details["frequency"],
                "end_date": schedule_details.get("end_date", ""),
                "active": True,
            })
            return query_id
        except ClientError as e:
            print(f"Error storing recurring query: {e}")
            return None
