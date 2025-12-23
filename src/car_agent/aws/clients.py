from __future__ import annotations

import boto3

from car_agent.config import Settings


def build_dynamodb(settings: Settings):
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def build_ses(settings: Settings):
    return boto3.client("ses", region_name=settings.aws_region)


def build_scheduler(settings: Settings):
    return boto3.client("scheduler", region_name=settings.aws_region)
