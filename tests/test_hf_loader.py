import pandas as pd
from persona_engine.hf_loader import numeric_ocean_columns, map_ocean_record, parse_ocean_value
from persona_engine.classifier import classify_persona_record

def test_ocean_columns_are_explicit_schema_fields():
    frame = pd.DataFrame({"openness": ["0.2"], "conscientiousness": ["0.3"], "text": ["a"]})
    assert numeric_ocean_columns(frame) == ["openness", "conscientiousness"]

def test_parse_numeric_and_label_ocean_values():
    assert parse_ocean_value("0.75 - 높음") == 0.75
    assert parse_ocean_value("높음") == 0.8
    assert parse_ocean_value("알 수 없음") is None

def test_map_ocean_record():
    row = pd.Series({"O": "0.1", "C": "0.2", "E": "0.3", "A": "0.4", "N": "0.5"})
    mapped = map_ocean_record(row, {
        "openness":"O", "conscientiousness":"C", "extraversion":"E",
        "agreeableness":"A", "neuroticism":"N"
    })
    assert mapped["neuroticism"] == 0.5

def test_base_persona_uses_text_fallback_without_ocean():
    result = classify_persona_record({
        "professional_persona": "품질 분석과 데이터 연구를 수행하는 엔지니어",
        "occupation": "품질 엔지니어"
    })
    assert result["method"] == "keyword_text_heuristic"
    assert result["role"] in {"Analytical", "Procedural", "Situational", "Control"}

def test_unknown_persona_does_not_invent_ocean_traits():
    result = classify_persona_record({"persona": "일반적인 생활 방식"})
    assert result["role"] == "General"
    assert result["confidence"] == "low"

def test_persona_sanitizer_excludes_demographic_and_health_fields():
    from persona_engine.hf_loader import sanitize_persona_frame
    frame = pd.DataFrame({
        "professional_persona":["공정 엔지니어"],
        "openness":["0.8"],
        "age":[35],
        "sex":["여자"],
        "blood_pressure_status":["정상"]
    })
    safe = sanitize_persona_frame(frame)
    assert "professional_persona" in safe.columns
    assert "openness" in safe.columns
    assert "age" not in safe.columns
    assert "sex" not in safe.columns
    assert "blood_pressure_status" not in safe.columns
