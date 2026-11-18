from __future__ import annotations

LENSES = {
 "analytical": {"name":"분석 에이전트", "questions":["설비의 회전·이동 상태는 무엇인가?","위험요인의 직접 원인과 선행조건은 무엇인가?","센서값 또는 작업상태의 이상 변화가 있는가?"]},
 "procedural": {"name":"절차 에이전트", "questions":["작업허가가 승인되었는가?","정지·에너지 차단·LOTO가 확인되었는가?","표준작업 및 점검기록이 존재하는가?"]},
 "situational": {"name":"현장상황 에이전트", "questions":["작업자와 위험구역의 위치가 겹치는가?","조도·시야·소음·교대 인수인계에 문제가 있는가?","보호구와 대피 경로가 확보되었는가?"]},
 "control": {"name":"작업통제 에이전트", "questions":["출입통제와 감시자가 배치되었는가?","동시작업 및 장비 이동 동선이 분리되었는가?","경보가 담당자에게 전달되고 확인되었는가?"]}
}

def review_scenario(scenario: dict, evidence: dict | None = None) -> list[dict]:
    evidence = evidence or {}
    results = []
    for key, lens in LENSES.items():
        findings = []
        if key == "procedural" and scenario.get("maintenance_active") and not scenario.get("loto_confirmed"):
            findings.append("정비 작업 중 LOTO 확인이 되지 않았습니다.")
        if key == "analytical" and scenario.get("equipment"):
            findings.append(f"{scenario['equipment']}의 정지·가드·운전상태 확인이 필요합니다.")
        if key == "situational" and scenario.get("worker_in_zone"):
            findings.append("작업자가 위험구역에 진입한 상태입니다.")
        if key == "control" and scenario.get("access_control") is False:
            findings.append("위험구역 출입통제가 확인되지 않았습니다.")
        results.append({"agent":lens["name"], "lens":key, "questions":lens["questions"], "findings":findings or ["현재 입력만으로 확정된 위반사항 없음 — 현장 확인 필요"]})
    return results
