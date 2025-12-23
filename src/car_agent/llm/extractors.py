from __future__ import annotations

from typing import Any, Dict

from langchain_core.output_parsers import JsonOutputParser

from car_agent.llm.prompts import car_criteria_prompt, schedule_prompt
from car_agent.schemas import CarCriteria, ScheduleDetails


def extract_car_criteria(llm, user_input: str) -> Dict[str, Any]:
    parser = JsonOutputParser(pydantic_object=CarCriteria)
    chain = car_criteria_prompt() | llm | parser

    result = chain.invoke({
        "input": user_input,
        "format_instructions": parser.get_format_instructions(),
    })

    return {k: v for k, v in result.items() if v is not None}


def extract_schedule_details(llm, user_input: str) -> Dict[str, Any]:
    parser = JsonOutputParser(pydantic_object=ScheduleDetails)
    chain = schedule_prompt() | llm | parser

    result = chain.invoke({
        "input": user_input,
        "format_instructions": parser.get_format_instructions(),
    })

    return {k: v for k, v in result.items() if v is not None}
