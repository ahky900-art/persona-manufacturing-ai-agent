from __future__ import annotations
from typing import Any
from persona_engine.hf_loader import ocean_profile_from_record

OCEAN_KEYS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")

ROLE_RULES = {
    "Analytical": {"focus": "원인·메커니즘·이상 징후", "agent": "analytical"},
    "Procedural": {"focus": "작업허가·LOTO·표준 준수", "agent": "procedural"},
    "Situational": {"focus": "작업자 보호·환경·인수인계", "agent": "situational"},
    "Control": {"focus": "작업구역 통제·감독·동시작업", "agent": "control"},
    "General": {"focus": "네 관점을 균형 있게 검토", "agent": "multi_review"},
}

def classify_ocean(ocean: dict[str, Any]) -> dict[str, str]:
    """Experimental mapping from OCEAN traits to review lenses; not a worker personality diagnosis."""
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
    return {"role": role, **ROLE_RULES[role], "confidence": f"{scores[role]:.2f}", "method": "experimental_ocean_rule"}

KEYWORDS = {
 "Analytical": ("분석", "데이터", "품질", "연구", "설계", "엔지니어", "공정개선", "diagnostic", "analysis"),
 "Procedural": ("정비", "보전", "설비관리", "품질관리", "검사", "운전원", "maintenance", "operator"),
 "Situational": ("보건", "안전", "교육", "상담", "간호", "복지", "인사", "human"),
 "Control": ("관리자", "감독", "생산관리", "현장관리", "팀장", "물류", "운송", "supervisor"),
}

def classify_persona_record(row: dict[str, Any]) -> dict[str, str]:
    """Use OCEAN only when all five attributes are present; otherwise classify text as a review context."""
    profile = ocean_profile_from_record(row)
    if profile:
        return classify_ocean(profile)
    text = " ".join(str(row.get(k, "")) for k in ("professional_persona", "persona", "occupation", "skills_and_expertise")).lower()
    scores = {role: sum(text.count(word.lower()) for word in words) for role, words in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return {"role":"General", **ROLE_RULES["General"], "confidence":"low", "method":"no_ocean_text_fallback"}
    total = sum(scores.values())
    return {"role":best, **ROLE_RULES[best], "confidence":f"{scores[best]/max(total,1):.2f}", "method":"keyword_text_heuristic"}
