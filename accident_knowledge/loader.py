from pathlib import Path
import pandas as pd

DEMO_PATH = Path(__file__).resolve().parents[1] / "data" / "sample" / "accidents.csv"
COLUMN_CANDIDATES = {
 "title": ["accident_title", "사고명", "재해명", "제목"],
 "description": ["description", "재해개요", "사고내용", "재해내용"],
 "cause": ["cause", "발생원인", "재해원인", "원인"],
 "prevention": ["prevention", "예방대책", "재발방지대책", "대책"],
 "equipment": ["equipment", "기인물", "설비명"],
 "hazard": ["hazard", "위험유형", "재해유형"]
}

def load_demo() -> pd.DataFrame:
    return pd.read_csv(DEMO_PATH)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for target, candidates in COLUMN_CANDIDATES.items():
        for col in candidates:
            if col in df.columns:
                rename[col] = target
                break
    out = df.rename(columns=rename).copy()
    for col in ["title","description","cause","prevention","equipment","hazard"]:
        if col not in out:
            out[col] = ""
    return out

def load_uploaded_csv(file) -> pd.DataFrame:
    return normalize_columns(pd.read_csv(file))
