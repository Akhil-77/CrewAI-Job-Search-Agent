"""Model router: tier -> LLM/model string. No model name outside config.py."""
import config
def get_llm(tier="cheap", economy=False):
    name = config.MODEL_TIERS["cheap" if economy else tier]
    try:
        from crewai import LLM
        return LLM(model=f"openai/{name}")
    except Exception:
        return name
def tier_for(agent_key, economy=False):
    if economy: return "cheap"
    return config.AGENT_TIER.get(agent_key, "cheap")
def max_iter_for(kind, economy=False):
    if economy: return config.MAX_ITER["writing"]
    return config.MAX_ITER.get(kind, 4)
