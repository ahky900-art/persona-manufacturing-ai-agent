from persona_engine.role_taxonomy import classify_work_persona
from accident_knowledge.focus_classifier import classify_accident_focus
from risk_engine.industrial_risk_catalog import EQUIPMENT, PATHS, WORK_SAFETY

def test_persona_role_is_explainable_and_uses_occupational_fields():
    result = classify_work_persona({
        "occupation":"설비보전 엔지니어",
        "professional_persona":"회전기계와 펌프 정비를 담당",
        "skills_and_expertise_list":"베어링 진동분석, 예방정비",
        "age":42,
        "sex":"남자",
        "healthcare_persona":""
    })
    assert result["primary"] == "equipment_maintenance"
    assert result["ranked"][0]["evidence"]
    assert "age" not in result["used_fields"]

def test_persona_unknown_is_not_forced_into_role():
    result=classify_work_persona({"sports_persona":"마라톤을 좋아함","age":32})
    assert result["primary"] == "unclassified"

def test_accident_focus_multi_tags_entanglement_and_loto():
    result=classify_accident_focus({
        "title":"회전 롤 이물 제거 중 끼임",
        "description":"설비 정지 없이 작업자가 회전부에 접근",
        "cause":"LOTO 미실시 및 방호장치 미확인",
        "prevention":"에너지 차단과 방호장치 확인"
    })
    assert result["primary"] == "끼임·말림·협착"
    assert any("끼임" in x["matched_terms"] for x in result["hits"])

def test_all_refractory_equipment_profiles_have_risk_paths():
    assert len(EQUIPMENT) == 11
    assert set(EQUIPMENT) == set(PATHS)
    assert all(len(paths) >= 3 for paths in PATHS.values())

def test_occupational_safety_is_separate_catalog():
    assert len(WORK_SAFETY) >= 5
    assert any("LOTO" in item["hard_alert"] for item in WORK_SAFETY)
