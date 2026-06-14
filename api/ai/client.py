import anthropic
from functools import lru_cache


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    # Reads ANTHROPIC_API_KEY from environment automatically
    return anthropic.Anthropic()
