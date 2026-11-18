from __future__ import annotations
import os
import pandas as pd

def load_hf_dataset(dataset_id: str, split: str = "train", token: str | None = None, limit: int = 5000) -> pd.DataFrame:
    """Load a user-selected Hugging Face dataset split; schema mapping stays explicit in the UI."""
    if not dataset_id or "/" not in dataset_id:
        raise ValueError("데이터셋 ID를 '조직명/데이터셋명' 형식으로 입력하세요.")
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("datasets 패키지가 필요합니다. pip install datasets") from exc
    resolved_token = token or os.getenv("HF_TOKEN") or None
    dataset = load_dataset(dataset_id, split=split, token=resolved_token)
    frame = dataset.select(range(min(len(dataset), limit))).to_pandas()
    if frame.empty:
        raise ValueError("선택한 split에 데이터가 없습니다.")
    return frame

def numeric_ocean_columns(frame: pd.DataFrame) -> list[str]:
    """Return numeric columns with values plausibly normalized to [0, 1]."""
    result = []
    for col in frame.columns:
        values = pd.to_numeric(frame[col], errors="coerce").dropna()
        if len(values) and values.between(0, 1).all():
            result.append(str(col))
    return result

def map_ocean_record(row, mapping: dict[str, str]) -> dict[str, float]:
    profile = {}
    for trait, column in mapping.items():
        value = pd.to_numeric(row[column], errors="coerce")
        if pd.isna(value):
            raise ValueError(f"{trait} 열 '{column}'에 숫자가 아닌 값이 있습니다.")
        profile[trait] = float(value)
    return profile
