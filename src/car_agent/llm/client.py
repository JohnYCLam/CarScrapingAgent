from __future__ import annotations

from langchain_openai import ChatOpenAI

from car_agent.config import Settings


def build_llm(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=settings.openai_api_key,
    )