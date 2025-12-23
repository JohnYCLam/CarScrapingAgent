from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


def car_criteria_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", """You are a car search criteria extractor. Extract ONLY fields explicitly mentioned.

Available fields: make, model, transmission, listing_type, year_min, year_max, mileage_max, price_max, location

Rules:
1. Only include a field if it's clearly mentioned
2. "from 2015 onward" => year_min=2015
3. "under $20000" => price_max=20000
4. transmission: "manual" or "automatic"
5. listing_type: "new" or "used"
6. Omit fields not mentioned
7. Return valid JSON only

{format_instructions}"""),
        ("human", "Extract car criteria from: {input}")
    ])


def schedule_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", """Extract scheduling information.

Fields:
- email
- frequency: EventBridge rate format (e.g., rate(1 day), rate(7 days))
- end_date: YYYY-MM-DD

Mappings:
- daily => rate(1 day)
- weekly => rate(7 days)
- every 3 days => rate(3 days)

{format_instructions}"""),
        ("human", "Extract scheduling info from: {input}")
    ])


def listing_batch_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", """You extract structured fields from used car listing texts.

For each listing, extract:
- make
- model
- year
- price
- mileage
- location

Rules:
- Only fill a field if explicitly present or strongly implied.
- Use integers for year/price/mileage.
- mileage is in km.
- Do not hallucinate missing data.

Return JSON matching:
{format_instructions}"""),
        ("user", "LISTINGS:\n{listing_block}")
    ])
