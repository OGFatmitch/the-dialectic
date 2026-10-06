from app.costs import estimate_response_cost, mode


def test_gpt_55_cost_includes_cached_tokens_and_tools():
    cost = estimate_response_cost("gpt-5.5", 1_000_000, 100_000, 200_000, 2)
    assert cost == 7.12


def test_modes_are_cost_ordered():
    assert mode("quick").baseline_estimate_usd < mode("standard").baseline_estimate_usd < mode("deep").baseline_estimate_usd
