from pathlib import Path
import pandas as pd

DEMO_PATH = Path(__file__).resolve().parents[1] / "data" / "sample" / "accidents.csv"
COLUMN_CANDIDATES = {
 "title": ["accident_title", "사고명", "재해명", "제목", "BBSCTT_SJ_NM"],
 "description": ["description", "재해개요", "사고내용", "재해내용", "BBSCTT_CN"],
 "cause": ["cause", "발생원인", "재해원인", "원인", "DSSTR_INDUCT_FCTR_CN"],
 "prevention": ["prevention", "예방대책", "재발방지대책", "대책", "RSKNSS_DCRS_CNTRPLN_CN"],
 "equipment": ["equipment", "기인물", "설비명", "관련설비", "작업설비"],
 "hazard": ["hazard", "위험유형", "재해형태", "재해유형", "발생형태"]
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
    last_error = None
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            file.seek(0)
            return normalize_columns(pd.read_csv(file, encoding=encoding))
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError(f"CSV 문자 인코딩을 판별하지 못했습니다(UTF-8/CP949 시도). {last_error}")
