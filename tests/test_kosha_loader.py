import pandas as pd
from accident_knowledge.loader import normalize_columns

def test_kosha_public_csv_schema_mapping():
    source = pd.DataFrame({
        "BBSCTT_SJ_NM": ["회전 롤 끼임"],
        "BBSCTT_CN": ["회전부 이물 제거 작업 중 사고"],
        "DSSTR_INDUCT_FCTR_CN": ["정지 및 에너지 차단 미확인"],
        "RSKNSS_DCRS_CNTRPLN_CN": ["LOTO 확인 및 가드 설치"]
    })
    normalized = normalize_columns(source)
    assert normalized.loc[0, "title"] == "회전 롤 끼임"
    assert normalized.loc[0, "description"] == "회전부 이물 제거 작업 중 사고"
    assert normalized.loc[0, "cause"] == "정지 및 에너지 차단 미확인"
    assert normalized.loc[0, "prevention"] == "LOTO 확인 및 가드 설치"
