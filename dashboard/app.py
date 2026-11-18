from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import streamlit as st
import pandas as pd
from persona_engine.classifier import classify_ocean
from risk_engine.scoring import calculate_risk
from agents.reviewers import review_scenario
from accident_knowledge.loader import load_demo, load_uploaded_csv
from ontology.graph import build_graph, graph_to_dot

st.set_page_config(page_title="Persona Manufacturing Safety Agent", page_icon="🦺", layout="wide")
st.title("🦺 Persona Manufacturing AI Safety Agent")
st.caption("제조 현장 위험요인 교차검토 · 온톨로지 · 야간 안전관제 | 연구용 MVP")

with st.sidebar:
    st.subheader("시나리오 입력")
    equipment = st.selectbox("설비", ["회전 롤", "천장크레인", "지게차", "로터리킬른", "소각로", "기타"])
    process = st.selectbox("작업", ["정비 작업", "이물 제거", "인양 작업", "운반 작업", "점검 작업"])
    hazard = st.selectbox("위험유형", ["끼임", "협착", "충돌", "추락", "화상", "분진"])
    maintenance = st.checkbox("정비 작업 진행 중", value=True)
    loto = st.checkbox("LOTO 확인 완료", value=False)
    worker_zone = st.checkbox("작업자 위험구역 진입", value=True)
    access = st.checkbox("출입통제 확인", value=False)
    st.divider()
    st.caption("현재 화면은 실제 PLC·센서에 연결되지 않은 데모입니다.")

scenario = {"equipment":equipment, "process":process, "hazard":hazard, "maintenance_active":maintenance,
            "loto_confirmed":loto, "worker_in_zone":worker_zone, "access_control":access}
risk_tab, persona_tab, agent_tab, ontology_tab, accident_tab, eval_tab = st.tabs(
    ["통합 관제", "Persona Lab", "Agent Control", "Ontology Graph", "사고 지식", "평가·한계"])

with risk_tab:
    risk = calculate_risk(5, 4, 4, 0.25, loto_confirmed=loto, maintenance_active=maintenance)
    a,b,c,d = st.columns(4)
    a.metric("위험점수 (데모)", risk.score)
    b.metric("위험등급", risk.level)
    c.metric("핵심 통제 실패", "예" if risk.hard_alert else "아니오")
    d.metric("현장 확인", "필요")
    if risk.hard_alert:
        st.error("긴급 확인: 정비 중 LOTO가 확인되지 않았습니다. 실제 작업을 즉시 안전절차에 따라 확인하십시오.")
    elif risk.score >= 35:
        st.warning("위험 수준이 높습니다. 담당 안전관리자의 현장 확인이 필요합니다.")
    st.subheader("현재 입력된 작업상태")
    st.json(scenario)
    st.caption("점수는 S=5, L=4, E=4, 통제효과=0.25인 데모 가정입니다. 실측값이 아닙니다.")

with persona_tab:
    st.subheader("OCEAN 기반 기능적 분석 관점")
    persona_path = Path(__file__).resolve().parents[1] / "data/sample/personas.json"
    personas = json.loads(persona_path.read_text(encoding="utf-8"))
    for p in personas:
        role = classify_ocean(p["ocean"])
        with st.expander(f'{p["persona_id"]} · {p["label"]} → {role["role"]}', expanded=True):
            st.write("분석 초점:", role["focus"])
            st.write("분류 점수(내부 규칙):", role["confidence"])
            st.json(p["ocean"])
    st.info("분류는 에이전트의 검토 관점을 배정할 뿐이며, 개인의 성격·사고확률·업무 적합성을 판단하지 않습니다. MBTI는 입력 데이터에 직접 존재한다고 가정하지 않습니다.")
    hf_id = st.text_input("선택적 Hugging Face 데이터셋 ID", value="")
    if st.button("Hugging Face 연결 안내"):
        st.info("데이터셋 ID를 확인하고 HF_DATASET_ID 및 필요 시 HF_TOKEN을 환경변수로 설정한 뒤 loader를 연결하세요. MVP는 외부 데이터 자동 다운로드를 수행하지 않습니다.")

with agent_tab:
    st.subheader("다중 에이전트 독립 검토")
    for result in review_scenario(scenario):
        with st.expander(result["agent"], expanded=True):
            st.markdown("**발견사항**")
            for item in result["findings"]:
                st.write("•", item)
            st.markdown("**검토 질문**")
            for q in result["questions"]:
                st.write("–", q)
    st.caption("에이전트는 규칙 기반 데모입니다. LLM 판정 또는 자동 작업중지 명령을 수행하지 않습니다.")

with ontology_tab:
    st.subheader("설비–공정–위험–사고–통제 온톨로지")
    graph = build_graph(scenario)
    st.graphviz_chart(graph_to_dot(graph), use_container_width=True)
    st.write(f"노드 {graph.number_of_nodes()}개 · 관계 {graph.number_of_edges()}개")
    st.caption("관계는 MVP의 개념 스키마이며 실제 사업장 데이터로 검증된 인과관계를 의미하지 않습니다.")

with accident_tab:
    st.subheader("산업재해 지식 데이터")
    uploaded = st.file_uploader("KOSHA 등 출처가 확인된 CSV 업로드", type=["csv"])
    try:
        accidents = load_uploaded_csv(uploaded) if uploaded else load_demo()
        st.dataframe(accidents, use_container_width=True)
        st.caption("업로드 데이터는 현재 세션에서만 사용합니다. 원본 이용조건과 출처를 반드시 확인하십시오.")
    except Exception as exc:
        st.error(f"CSV를 읽지 못했습니다: {exc}")
        accidents = load_demo()
    keyword = st.text_input("사례 검색", value=hazard)
    mask = accidents.astype(str).apply(lambda col: col.str.contains(keyword, case=False, na=False)).any(axis=1)
    st.dataframe(accidents[mask], use_container_width=True)

with eval_tab:
    st.subheader("검증 계획")
    st.markdown("""
- **페르소나:** 군집 분리도, 재현성, 전문가 검토 일치도
- **위험 탐지:** Precision, Recall, F1, PR-AUC, 치명위험 누락률
- **경보 운영:** 오경보율, 확인 소요시간, 야간 관리자 경보량
- **현장 효용:** 위험 발견률과 조치 리드타임의 개선 여부
    """)
    st.warning("사고사례만으로 정상상태 대비 사고확률을 학습할 수 없습니다. 정상 운전 데이터, 비사고 작업 이력, PLC·센서·작업허가·LOTO 정보가 추가로 필요합니다.")
    st.markdown("**운영 전 필수:** 산업안전 전문가 검토, 사업장 위험성평가 기준과 임계치 보정, 데이터 품질·결측·센서 신뢰도 검증, 접근권한 및 감사로그 설계.")
