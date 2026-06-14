import json

from .client import get_client
from .prompts import RECOMMENDATIONS_SYSTEM, SUMMARY_SYSTEM, CHAT_SYSTEM

MODEL = "claude-opus-4-8"

# cache_control applied to all static system prompts
_CACHE = {"type": "ephemeral"}

_REC_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title":       {"type": "string"},
                    "description": {"type": "string"},
                    "impact":      {"type": "string", "enum": ["alto", "medio", "baixo"]},
                },
                "required": ["title", "description", "impact"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["recommendations"],
    "additionalProperties": False,
}


def get_recommendations(analysis: dict) -> list[dict]:
    """Return 3–5 actionable SCI recommendations based on analysis data."""
    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[{"type": "text", "text": RECOMMENDATIONS_SYSTEM, "cache_control": _CACHE}],
        output_config={"format": {"type": "json_schema", "schema": _REC_SCHEMA}},
        messages=[{
            "role": "user",
            "content": f"Dados da análise SCI:\n{json.dumps(analysis, ensure_ascii=False, indent=2)}",
        }],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)["recommendations"]


def get_summary(analysis: dict) -> str:
    """Return a 2–3 sentence natural language summary of the SCI analysis."""
    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=[{"type": "text", "text": SUMMARY_SYSTEM, "cache_control": _CACHE}],
        messages=[{
            "role": "user",
            "content": f"Dados da análise SCI:\n{json.dumps(analysis, ensure_ascii=False, indent=2)}",
        }],
    )
    return next(b.text for b in response.content if b.type == "text").strip()


def chat(message: str, context: dict, history: list[dict]) -> str:
    """Answer a user question about their SCI analyses."""
    client = get_client()

    # Context is injected as a priming exchange so the system prompt stays
    # byte-identical (and cached) across all users.
    context_block = (
        f"Contexto do usuário no EcoDash:\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )
    messages = [
        {"role": "user",      "content": context_block},
        {"role": "assistant", "content": "Contexto carregado. Estou pronto para responder sobre suas análises SCI."},
        *history[-10:],  # last 5 turns max
        {"role": "user",      "content": message},
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[{"type": "text", "text": CHAT_SYSTEM, "cache_control": _CACHE}],
        messages=messages,
    )
    return next(b.text for b in response.content if b.type == "text").strip()
