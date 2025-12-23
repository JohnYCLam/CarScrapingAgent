from __future__ import annotations

import json
from typing import Any, Dict

from car_agent.agent import CarScraperAgent

agent = CarScraperAgent(enable_aws=True)


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    print(f"Raw event: {json.dumps(event, indent=2)}")  # DEBUG
    
    # Handle both direct test events AND API Gateway
    if "body" in event:
        body = event["body"]
        if isinstance(body, str):
            try:
                payload = json.loads(body)
                print(f"Parsed body: {json.dumps(payload, indent=2)}")  # DEBUG
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                payload = {}
        else:
            payload = body or {}
    else:
        payload = event

    user_id = payload.get("user_id", "anonymous")
    message = payload.get("message", "").strip()  # STRIP whitespace
    session_data = payload.get("session_data", {}) or {}
    
    print(f"Final inputs - user_id: {user_id}, message: '{message}', session_data keys: {list(session_data.keys())}")  # DEBUG
    
    result = agent.process_conversation(user_id=user_id, message=message, session_data=session_data)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # CORS
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(result),
    }
