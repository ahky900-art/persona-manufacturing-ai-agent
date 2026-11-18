from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import streamlit as st
import pandas as pd
from persona_engine.classifier import classify_ocean, classify_persona_record
from persona_engine.hf_loader import load_hf_dataset, load_uploaded_persona_csv, OCEAN_FIELDS
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
    st.caption("실제 PLC·센서·작업허가 시스템에는 연결되지 않은 데모입니다.")

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
        st.error("긴급 확인: 정비 중 LOTO가 확인되지 않았습니다. 실제 작업상태와 안전절차를 즉시 확인하십시오.")
    elif risk.score >= 35:
        st.warning("위험 수준이 높습니다. 담당 안전관리자의 현장 확인이 필요합니다.")
    st.subheader("현재 입력된 작업상태")
    st.json(scenario)
    st.caption("점수는 S=5, L=4, E=4, 통제효과=0.25인 데모 가정입니다. 실측값이 아닙니다.")

with persona_tab:
    st.subheader("Hugging Face 페르소나 데이터")
    st.markdown("기본 데이터셋에는 OCEAN 점수 열이 없을 수 있습니다. Extended 데이터셋에서 다섯 특성이 확인될 때만 OCEAN 규칙을 적용하며, 그렇지 않으면 직업·전문성 서술로 검토 관점을 분류합니다.")
    extended_upload = st.file_uploader("NVIDIA Nemotron-Personas-Korea-Extended CSV (선택)", type=["csv"], key="extended_persona_csv")
    if extended_upload is not None:
        try:
            frame = load_uploaded_persona_csv(extended_upload)
            st.session_state["hf_personas"] = frame
            st.session_state["persona_source"] = "Nemotron-Personas-Korea-Extended CSV"
            st.success("Extended CSV를 불러왔습니다. 안전 필터링 후 OCEAN 필드를 확인합니다.")
        except Exception as exc:
            st.error(f"Extended CSV 로딩 실패: {exc}")
    hf_id = st.text_input("기본 Hugging Face Dataset ID", value="nvidia/Nemotron-Personas-Korea")
    hf_split = st.text_input("Split", value="train")
    hf_limit = st.number_input("최대 로딩 행 수", min_value=50, max_value=10000, value=500, step=50)
    if st.button("페르소나 데이터 불러오기"):
        try:
            frame = load_hf_dataset(hf_id, hf_split, limit=int(hf_limit))
            st.session_state["hf_personas"] = frame
            st.session_state["persona_source"] = "Hugging Face base dataset"
            st.session_state.pop("persona_results", None)
            st.success(f"{len(frame):,}개 샘플을 불러왔습니다. 이름·성별·연령·건강 등 개인/민감 속성은 화면 분석에서 제외했습니다.")
        except Exception as exc:
            st.error(f"데이터셋 로딩 실패: {exc}")
    frame = st.session_state.get("hf_personas")
    if frame is not None:
        st.caption("데이터 출처: " + st.session_state.get("persona_source", "업로드/세션 데이터"))
        st.write("안전 필터링 후 데이터 미리보기")
        st.dataframe(frame.head(8), use_container_width=True)
        available_ocean = [field for field in OCEAN_FIELDS if field in frame.columns]
        if len(available_ocean) == 5:
            st.success("OCEAN 5개 속성이 모두 확인되었습니다. 실제 값 파싱 후 분류합니다.")
        else:
            st.info(f"현재 데이터셋에서 OCEAN 필드 {len(available_ocean)}/5개 확인. OCEAN 점수 분류 대신 직업·전문성 텍스트 기반 기능 관점 분류를 적용합니다.")
        if st.button("기능적 분석 관점 분류 실행"):
            rows = []
            for idx, row in frame.iterrows():
                record = row.to_dict()
                result = classify_persona_record(record)
                rows.append({
                    "row": int(idx),
                    "role": result["role"],
                    "focus": result["focus"],
                    "confidence": result["confidence"],
                    "method": result["method"],
                    "occupation": record.get("occupation", ""),
                    "professional_persona": record.get("professional_persona", "")
                })
            result_frame = pd.DataFrame(rows)
            st.session_state["persona_results"] = result_frame
        if "persona_results" in st.session_state:
            result_frame = st.session_state["persona_results"]
            st.dataframe(result_frame, use_container_width=True)
            st.download_button("분류 결과 CSV 다운로드", result_frame.to_csv(index=False).encode("utf-8-sig"), "persona_review_lenses.csv", "text/csv")
            st.caption("이 결과는 안전 검토 관점 배정용 실험적 분류이며, 실제 근로자 성격·사고확률·업무 적합성 평가가 아닙니다.")
    else:
        st.info("기본 데모 페르소나 4종은 외부 데이터 연결 없이도 Agent Control에서 사용할 수 있습니다.")

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
    try:
        accidents_for_graph = load_demo()
        graph = build_graph(scenario, accidents_for_graph)
        st.graphviz_chart(graph_to_dot(graph), use_container_width=True)
        st.write(f"노드 {graph.number_of_nodes()}개 · 관계 {graph.number_of_edges()}개")
    except Exception as exc:
        st.error(f"온톨로지 그래프 생성 실패: {exc}")
    st.caption("사고사례와 예방대책은 연결 후보로 표시합니다. 그래프의 연결은 통계적·물리적 인과관계가 검증되었다는 뜻이 아닙니다.")

with accident_tab:
    st.subheader("산업재해 지식 데이터")
    uploaded = st.file_uploader("출처가 확인된 KOSHA CSV 업로드", type=["csv"])
    try:
        accidents = load_uploaded_csv(uploaded) if uploaded else load_demo()
        st.write(f"총 {len(accidents):,}건")
        st.dataframe(accidents, use_container_width=True)
        st.caption("업로드 데이터는 현재 세션에서만 사용합니다. 원본 이용조건과 출처를 확인하십시오.")
    except Exception as exc:
        st.error(f"CSV를 읽지 못했습니다: {exc}")
        accidents = load_demo()
    keyword = st.text_input("사례 검색", value=hazard)
    mask = accidents.astype(str).apply(lambda col: col.str.contains(keyword, case=False, na=False)).any(axis=1)
    st.dataframe(accidents[mask], use_container_width=True)

with eval_tab:
    st.subheader("검증 계획")
    st.markdown("""
- **페르소나:** 데이터 필드 매핑 성공률, 분류 안정성, 전문가 검토 일치도
- **위험 탐지:** Precision, Recall, F1, PR-AUC, 치명위험 누락률
- **경보 운영:** 오경보율, 확인 소요시간, 야간 관리자 경보량
- **현장 효용:** 위험 발견률과 조치 리드타임의 개선 여부
    """)
    st.warning("사고사례만으로 정상상태 대비 사고확률을 학습할 수 없습니다. 정상 운전 데이터, 비사고 작업 이력, PLC·센서·작업허가·LOTO 정보가 추가로 필요합니다.")
    st.markdown("**운영 전 필수:** 산업안전 전문가 검토, 사업장 위험성평가 기준과 임계치 보정, 데이터 품질·결측·센서 신뢰도 검증, 접근권한 및 감사로그 설계.")
