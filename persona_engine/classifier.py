from __future__ import annotations
from typing import Any

OCEAN_KEYS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")

ROLE_RULES = {
    "Analytical": {"focus": "원인·메커니즘·이상 징후", "agent": "analytical"},
    "Procedural": {"focus": "작업허가·LOTO·표준 준수", "agent": "procedural"},
    "Situational": {"focus": "작업자 보호·환경·인수인계", "agent": "situational"},
    "Control": {"focus": "작업구역 통제·감독·동시작업", "agent": "control"},
}

def classify_ocean(ocean: dict[str, Any]) -> dict[str, str]:
    """Map OCEAN profiles to functional review lenses, not worker risk labels."""
    values = {k: float(ocean.get(k, 0.5)) for k in OCEAN_KEYS}
    if any(v < 0 or v > 1 for v in values.values()):
        raise ValueError("OCEAN 값은 0~1 범위여야 합니다.")
    scores = {
        "Analytical": values["openness"] * 0.55 + (1-values["extraversion"]) * 0.20 + values["conscientiousness"] * 0.25,
        "Procedural": values["conscientiousness"] * 0.70 + (1-values["openness"]) * 0.15 + (1-values["neuroticism"]) * 0.15,
        "Situational": values["agreeableness"] * 0.45 + values["neuroticism"] * 0.15 + (1-values["extraversion"]) * 0.10 + values["openness"] * 0.30,
        "Control": values["extraversion"] * 0.45 + values["conscientiousness"] * 0.40 + (1-values["agreeableness"]) * 0.15,
    }
    role = max(scores, key=scores.get)
    return {"role": role, **ROLE_RULES[role], "confidence": f"{scores[role]:.2f}"}
