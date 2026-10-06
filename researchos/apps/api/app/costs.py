from dataclasses import dataclass


RATE_CARD_VERSION = "openai-2026-10-06"
MODEL_RATES = {"gpt-5.5": {"input": 5.00, "cached": 0.50, "output": 30.00}}
WEB_SEARCH_PER_CALL = 0.01


@dataclass(frozen=True)
class SearchMode:
    name: str
    query_limit: int
    context_size: str
    candidate_limit: int
    baseline_estimate_usd: float


SEARCH_MODES = {
    "quick": SearchMode("quick", 2, "low", 3, 0.30),
    "standard": SearchMode("standard", 5, "medium", 5, 0.85),
    "deep": SearchMode("deep", 5, "high", 5, 2.50),
}


def mode(name: str) -> SearchMode:
    if name not in SEARCH_MODES:
        raise ValueError(f"Unknown search mode: {name}")
    return SEARCH_MODES[name]


def estimate_response_cost(model: str, input_tokens: int, output_tokens: int, cached_tokens: int, tool_calls: int) -> float:
    rates = MODEL_RATES.get(model)
    if not rates:
        return 0.0
    ordinary = max(0, input_tokens - cached_tokens)
    cost = ordinary * rates["input"] / 1_000_000
    cost += cached_tokens * rates["cached"] / 1_000_000
    cost += output_tokens * rates["output"] / 1_000_000
    cost += tool_calls * WEB_SEARCH_PER_CALL
    return round(cost, 6)
