from __future__ import annotations
from itertools import islice
import os
import re
import pandas as pd

OCEAN_FIELDS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")
SAFE_PERSONA_FIELDS = {
    "uuid", "professional_persona", "sports_persona", "arts_persona", "travel_persona",
    "culinary_persona", "family_persona", "persona", "cultural_background",
    "skills_and_expertise", "skills_and_expertise_list", "hobbies_and_interests",
    "hobbies_and_interests_list", "career_goals_and_ambitions", "occupation",
    *OCEAN_FIELDS
}

def load_hf_dataset(dataset_id: str, split: str = "train", token: str | None = None, limit: int = 2000) -> pd.DataFrame:
    """Stream a bounded sample and retain only work/persona/OCEAN fields."""
    if not dataset_id or "/" not in dataset_id:
        raise ValueError("데이터셋 ID를 '조직명/데이터셋명' 형식으로 입력하세요.")
    if limit < 1:
        raise ValueError("limit는 1 이상이어야 합니다.")
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("datasets 패키지가 필요합니다. pip install datasets") from exc
    resolved_token = token or os.getenv("HF_TOKEN") or None
    stream = load_dataset(dataset_id, split=split, streaming=True, token=resolved_token)
    records = list(islice(iter(stream), int(limit)))
    if not records:
        raise ValueError("선택한 split에서 레코드를 가져오지 못했습니다.")
    frame = pd.DataFrame.from_records(records)
    safe_columns = [col for col in frame.columns if col in SAFE_PERSONA_FIELDS]
    return frame.loc[:, safe_columns].copy()

def sanitize_persona_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep only approved work/persona fields, including from user-uploaded Extended CSVs."""
    return frame.loc[:, [col for col in frame.columns if col in SAFE_PERSONA_FIELDS]].copy()

def load_uploaded_persona_csv(file) -> pd.DataFrame:
    last_error = None
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            file.seek(0)
            return sanitize_persona_frame(pd.read_csv(file, encoding=encoding))
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError(f"CSV 문자 인코딩을 판별하지 못했습니다(UTF-8/CP949 시도). {last_error}")

def parse_ocean_value(value) -> float | None:
    """Parse explicit numeric values or descriptive OCEAN labels; unknown text stays unknown."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    matches = re.findall(r"(?<![A-Za-z])(?:0?\.\d+|1(?:\.0+)?|[1-9]\d?)(?![A-Za-z])", text)
    for token in matches:
        try:
            number = float(token)
        except ValueError:
            continue
        if 0 <= number <= 1:
            return number
        if 1 < number <= 100:
            return number / 100.0
    lowered = text.lower()
    if any(word in lowered for word in ("매우 높", "높음", "high", "높은")):
        return 0.8
    if any(word in lowered for word in ("매우 낮", "낮음", "low", "낮은")):
        return 0.2
    if any(word in lowered for word in ("보통", "중간", "medium", "moderate")):
        return 0.5
    return None

def ocean_profile_from_record(row) -> dict[str, float] | None:
    values = {trait: parse_ocean_value(row.get(trait)) for trait in OCEAN_FIELDS}
    return values if all(value is not None for value in values.values()) else None

def numeric_ocean_columns(frame: pd.DataFrame) -> list[str]:
    return [field for field in OCEAN_FIELDS if field in frame.columns]

def map_ocean_record(row, mapping: dict[str, str]) -> dict[str, float]:
    profile = {}
    for trait, column in mapping.items():
        value = parse_ocean_value(row[column])
        if value is None:
            raise ValueError(f"{trait} 열 '{column}'에서 점수/라벨을 해석하지 못했습니다: {row[column]}")
        profile[trait] = value
    return profile
