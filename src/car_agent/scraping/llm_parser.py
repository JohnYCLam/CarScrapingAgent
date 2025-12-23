from __future__ import annotations

from typing import Dict, List

from langchain_core.output_parsers import JsonOutputParser

from car_agent.llm.prompts import listing_batch_prompt
from car_agent.schemas import ListingsBatch


def parse_listings_with_llm(llm, listing_texts: List[str]) -> List[Dict]:
    if not listing_texts:
        return []

    parser = JsonOutputParser(pydantic_object=ListingsBatch)
    prompt = listing_batch_prompt()

    numbered = []
    for i, txt in enumerate(listing_texts):
        snippet = (txt or "").strip()
        if len(snippet) > 1500:
            snippet = snippet[:1500]
        numbered.append(f"[{i}] {snippet}")

    listing_block = "\n\n".join(numbered)

    chain = prompt | llm | parser
    result = chain.invoke({
        "listing_block": listing_block,
        "format_instructions": parser.get_format_instructions(),
    })

    parsed_list = []
    for info in result.get("listings", []):
        clean = {k: v for k, v in info.items() if v is not None}
        parsed_list.append(clean)

    if len(parsed_list) < len(listing_texts):
        parsed_list.extend({} for _ in range(len(listing_texts) - len(parsed_list)))

    return parsed_list
