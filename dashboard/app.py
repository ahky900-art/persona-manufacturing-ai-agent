from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
from persona_engine.hf_loader import load_hf_dataset, load_uploaded_persona_csv, OCEAN_FIELDS
from persona_engine.role_taxonomy import ROLE_DEFINITIONS, classify_work_persona
from accident_knowledge.loader import load_demo, load_uploaded_csv, normalize_columns
from accident_knowledge.focus_classifier import classify_accident_focus, RULES
from risk_engine.industrial_risk_catalog import EQUIPMENT, PATHS, WORK_SAFETY
from risk_engine.scoring import calculate_risk

st.set_page_config(page_title="Persona Manufacturing AI Safety Agent", page_icon="🦺", layout="wide")
st.title("🦺 Persona Manufacturing AI Safety Agent")
st.caption("합성 페르소나의 직무 관점 → 산업재해 포커스 → 제조설비 위험경로 → 관측 신호 | 연구용 MVP")

with st.sidebar:
    st.subheader("분석 대상")
    equipment_key = st.selectbox("산업설비", list(EQUIPMENT), format_func=lambda k:EQUIPMENT[k], index=0)
    st.divider()
    st.caption("위험 경로는 ahky900-art/refractory의 설비별 온톨로지·정비 프로파일을 바탕으로 구성했습니다.")
    st.caption("센서·PLC·작업허가 실시간 연동은 아직 없습니다.")

tabs=st.tabs(["전체 구조","Persona 분류 기준","사고 포커스","산업현장 Risk","작업자 안전 Risk","온톨로지 경로","검증·출처"])

with tabs[0]:
    st.subheader("시스템 작동 구조")
    st.graphviz_chart("""
    digraph G {
      rankdir=LR; node [shape=box,style="rounded,filled",fillcolor="#eaf1f8"];
      A[label="Hugging Face\nPersona fields"]; B[label="Work-function roles\n근거 키워드·가중치"];
      C[label="KOSHA cases\n사고 제목·개요·원인·대책"]; D[label="Accident focus\n다중 태깅"];
      E[label="Refractory industry\n11 equipment profiles"]; F[label="Process condition\n운전·정비 인자"];
      G[label="Damage mechanism\n열·화학·기계"]; H[label="Monitoring signals\n관측 후보"]; I[label="Alert & control\n관리자 검토"];
      A->B; C->D; B->D[label="review lens"]; D->F; E->F; F->G->H->I;
    }
    """,use_container_width=True)
    a,b,c=st.columns(3)
    a.metric("산업설비 프로파일",len(EQUIPMENT))
    b.metric("기능적 페르소나",len(ROLE_DEFINITIONS))
    c.metric("사고 포커스 태그",len(RULES))
    st.info("핵심 원칙: Persona는 무엇을 먼저 검토할지 제안합니다. 위험 등급은 실제 작업·설비 데이터로 별도 산출해야 하며 Persona 점수로 사고확률을 계산하지 않습니다.")

with tabs[1]:
    st.subheader("Hugging Face 데이터 → 기능적 Persona 분류")
    st.markdown("**분류 대상은 합성 인물의 직무 맥락입니다.** 성격 유형(MBTI)이나 근로자 개인의 안전행동을 진단하지 않습니다.")
    st.markdown("기본 데이터셋 또는 NVIDIA Extended CSV를 불러온 뒤, 레코드별 분류 근거를 확인할 수 있습니다.")
    upload=st.file_uploader("Nemotron-Personas-Korea-Extended CSV 업로드(선택)",type=["csv"],key="persona_csv")
    if upload is not None:
        try:
            st.session_state["personas"]=load_uploaded_persona_csv(upload)
            st.session_state["persona_source"]="NVIDIA Extended CSV"
            st.success("CSV 로딩 완료. 분석에 허용된 직무·전문성 필드만 남겼습니다.")
        except Exception as exc:
            st.error(f"CSV 로딩 실패: {exc}")
    with st.expander("Hugging Face 기본 데이터셋에서 불러오기"):
        dsid=st.text_input("Dataset ID",value="nvidia/Nemotron-Personas-Korea")
        split=st.text_input("Split",value="train")
        limit=st.number_input("최대 샘플",min_value=20,max_value=5000,value=300,step=20)
        if st.button("기본 페르소나 불러오기"):
            try:
                st.session_state["personas"]=load_hf_dataset(dsid,split,limit=int(limit))
                st.session_state["persona_source"]="Hugging Face base dataset"
                st.success(f"{len(st.session_state['personas']):,}건을 스트리밍으로 불러왔습니다.")
            except Exception as exc:
                st.error(f"로딩 실패: {exc}")
    st.markdown("#### 필드별 분류 가중치")
    weights={"occupation":4,"professional_persona":4,"skills_and_expertise_list":3,"skills_and_expertise":2,"detailed_persona":2,"career_goals_and_ambitions":1,"persona":1}
    st.dataframe(pd.DataFrame([{"필드":k,"가중치":v,"역할": "직업·전문성 근거" if v>=2 else "보조 근거"} for k,v in weights.items()]),use_container_width=True,hide_index=True)
    st.caption("점수 = 필드 가중치 × 해당 필드에서 일치한 직무 키워드 수. 복수 역할을 허용하며 일치 키워드와 원본 필드를 공개합니다.")
    st.markdown("#### 역할 정의")
    for key,definition in ROLE_DEFINITIONS.items():
        with st.expander(definition["label"]):
            st.write("**집중 관점:**",definition["focus"])
            st.write("**사고 검토 렌즈:**",definition["incident_lens"])
            st.write("**대표 키워드:**",", ".join(definition["keywords"]))
            st.write("**검토 질문:**")
            for q in definition["questions"]: st.write("•",q)
    frame=st.session_state.get("personas")
    if frame is not None and not frame.empty:
        st.caption("데이터 출처: "+st.session_state.get("persona_source",""))
        st.write("허용된 직무·전문성 필드 미리보기")
        st.dataframe(frame.head(10),use_container_width=True)
        if st.button("전체 레코드 역할 분류"):
            rows=[]
            for ix,row in frame.iterrows():
                result=classify_work_persona(row.to_dict())
                for rank,item in enumerate(result["ranked"],start=1):
                    rows.append({"row":int(ix),"순위":rank,"역할":item["label"],"점수":item["score"],"비중":item["share"],"집중 관점":item["focus"],"사고 검토 렌즈":item["incident_lens"],"근거":", ".join(x["field"]+":"+x["keyword"] for x in item["evidence"][:8])})
                if not result["ranked"]:
                    rows.append({"row":int(ix),"순위":None,"역할":"미분류","점수":0,"비중":0,"집중 관점":"근거 부족","사고 검토 렌즈":"일반 검토","근거":"직무 키워드 매칭 없음"})
            st.session_state["role_results"]=pd.DataFrame(rows)
        if "role_results" in st.session_state:
            res=st.session_state["role_results"]
            st.dataframe(res,use_container_width=True)
            st.download_button("Persona 분류 CSV 다운로드",res.to_csv(index=False).encode("utf-8-sig"),"persona_role_results.csv","text/csv")
    else:
        st.info("데이터를 불러오기 전에도 위 역할 정의와 가중치 기준을 확인할 수 있습니다.")
    st.warning("OCEAN 5개 필드는 직무 분류에 사용하지 않습니다. Extended의 건강·성별·연령·소득·가족 등 인구통계 속성도 위험 점수와 역할 배정에서 제외합니다.")

with tabs[2]:
    st.subheader("KOSHA 사고사례 → 사고 포커스")
    st.markdown("사고 제목·발생 개요·발생 원인·예방대책의 텍스트에서 위험 키워드를 다중 태깅합니다. 사례의 사고 유형을 분류하는 규칙이며 발생확률 모델은 아닙니다.")
    st.markdown("#### 공공데이터포털 API 연결")
    st.caption("API 인증키는 코드에 저장하지 않습니다. Render/Streamlit Secrets에 KOSHA_SERVICE_KEY를 등록하세요. 요청주소는 기본값이 설정되어 있으며 필요할 때만 KOSHA_API_URL로 덮어씁니다.")
    try:
        from accident_knowledge.openapi_client import fetch_public_api, load_env_params
        import os
        api_ready=bool(os.getenv("KOSHA_SERVICE_KEY"))
        if api_ready:
            if st.button("실제 산재 API 조회",key="fetch_kosha_api"):
                try:
                    api_frame,api_meta=fetch_public_api(params=load_env_params())
                    st.session_state["kosha_api_frame"]=api_frame
                    st.session_state["kosha_api_meta"]=api_meta
                    st.success(f"API 응답 성공: {len(api_frame):,}건 · {api_meta['format']}")
                except Exception as api_exc:
                    st.error(f"API 조회 실패: {api_exc}")
        else:
            st.warning("API 연결 설정이 아직 완료되지 않았습니다. 제공해주신 URL은 공공데이터포털의 활용신청 계정 화면이며, 실제 API 요청주소가 아닙니다. API 명세의 '요청주소'와 서비스키를 서버 환경변수로 등록해야 합니다.")
        if "kosha_api_frame" in st.session_state:
            api_frame=st.session_state["kosha_api_frame"]
            st.metric("API에서 가져온 행",len(api_frame))
            st.caption("응답 형식: "+str(st.session_state.get("kosha_api_meta",{}).get("format","")))
    except Exception as api_setup_exc:
        st.info(f"API 연결 모듈 초기화: {api_setup_exc}")
    upload_acc=st.file_uploader("KOSHA 제조업 사고사례 CSV 업로드(대체 경로)",type=["csv"],key="kosha_csv")
    try:
        cases=load_uploaded_csv(upload_acc) if upload_acc else load_demo()
    except Exception as exc:
        st.error(f"사고 데이터 로딩 오류: {exc}")
        cases=load_demo()
    tagged=[]
    for ix,row in cases.iterrows():
        result=classify_accident_focus(row.to_dict())
        tagged.append({"row":int(ix),"title":row.get("title",""),"cause":row.get("cause",""),"prevention":row.get("prevention",""),"primary_focus":result["primary"],"all_focus":", ".join(x["label"] for x in result["hits"]),"matched_terms":", ".join(sorted(set(w for x in result["hits"] for w in x["matched_terms"])))})
    tagged_df=pd.DataFrame(tagged)
    c1,c2=st.columns(2)
    c1.metric("사고사례",len(cases))
    c2.metric("분류된 사례",int((tagged_df["primary_focus"]!="미분류").sum()))
    focus_filter=st.selectbox("사고 포커스 필터",["전체"]+list(RULES))
    view=tagged_df if focus_filter=="전체" else tagged_df[tagged_df["all_focus"].str.contains(focus_filter,regex=False)]
    st.dataframe(view,use_container_width=True,hide_index=True)
    st.download_button("사고 포커스 결과 CSV",tagged_df.to_csv(index=False).encode("utf-8-sig"),"kosha_accident_focus.csv","text/csv")
    for label,words in RULES.items():
        with st.expander(label):
            st.write("**키워드:**",", ".join(words))
            matched=tagged_df[tagged_df["all_focus"].str.contains(label,regex=False)]
            st.write(f"태깅 사례 {len(matched)}건")
    st.caption("KOSHA 원본의 네 필드명은 로더에서 title/description/cause/prevention으로 정규화합니다. 출처와 이용조건은 원본 데이터 기준으로 유지하십시오.")

with tabs[3]:
    st.subheader(EQUIPMENT[equipment_key]+" · 설비 열화/손상 위험")
    st.markdown("아래 경로는 refractory 저장소의 설비별 온톨로지와 정비 위험 프로파일을 구조화한 것입니다.")
    paths=PATHS.get(equipment_key,[])
    st.metric("등록된 위험 경로",len(paths))
    for i,item in enumerate(paths,1):
        with st.expander(f"{i}. {item['driver']} → {item['damage']}",expanded=(i==1)):
            st.write("**변화 방향:**",item["change"])
            st.write("**공정 상태 변화:**",item["state"])
            st.write("**손상 메커니즘:**",item["mechanism"])
            st.write("**취약 부위:**",item["zone"])
            st.write("**성립 조건·주의:**",item["condition"])
            st.write("**근거 연결:**",item["evidence"])
            st.write("**관측 신호 후보:**")
            for sig in item["monitor"]: st.write("•",sig)
    st.warning("관측 신호는 후보 지표입니다. 현장 센서가 해당 변수를 측정하는지, 손상과 시간적으로 선행하는지 검증 전에는 예측 변수로 간주하지 않습니다.")

with tabs[4]:
    st.subheader("작업자 안전 위험 — 설비 열화 위험과 별도 관리")
    st.markdown("이 영역은 KOSHA 사고사례의 작업·위험 태그와 일반적인 핵심 통제 확인 항목을 연결한 체크리스트입니다. 작업자 위치·LOTO·가스측정 등 실제 입력이 없으면 감지된 것으로 표시하지 않습니다.")
    for item in WORK_SAFETY:
        with st.expander(item["task"]+" · "+item["hazard"]):
            st.write("**위험 트리거:**")
            for t in item["triggers"]: st.write("•",t)
            st.write("**핵심 통제:**")
            for c in item["controls"]: st.write("•",c)
            st.error("별도 즉시 확인 조건: "+item["hard_alert"])
    st.info("작업자 안전 위험은 내화물 잔여두께·쉘 온도 같은 설비건전성 지표와 별도 점수체계로 관리해야 합니다.")

with tabs[5]:
    st.subheader("설비별 온톨로지 경로")
    st.caption("인자 변화 → 공정 상태 → 손상 메커니즘 → 손상 결과 → 취약 부위 → 관측 신호")
    selected=st.selectbox("위험 경로 선택",range(len(PATHS[equipment_key])),format_func=lambda n:PATHS[equipment_key][n]["driver"]+" → "+PATHS[equipment_key][n]["damage"],key="path_select")
    p=PATHS[equipment_key][selected]
    st.graphviz_chart(f'''
    digraph RiskPath {{
      rankdir=LR; node [shape=box,style="rounded,filled",fontname="Arial"];
      A [label="{p["driver"]}",fillcolor="#dceaf7",style="rounded,filled"];
      B [label="{p["state"]}",fillcolor="#e9e4f7",style="rounded,filled"];
      C [label="{p["mechanism"]}",fillcolor="#f9e7cc",style="rounded,filled"];
      D [label="{p["damage"]}",fillcolor="#f5dada",style="rounded,filled"];
      E [label="{p["zone"]}",fillcolor="#dcefe4",style="rounded,filled"];
      A->B->C->D->E;
    }}
    ''',use_container_width=True)
    st.write("**성립 조건:**",p["condition"])
    st.write("**관측 신호 후보:**",", ".join(p["monitor"]))
    st.write("**근거:**",p["evidence"])
    st.caption("관계는 문헌/설비 지식 기반의 조건부 가설입니다. 인과 크기나 발생확률을 의미하지 않습니다.")

with tabs[6]:
    st.subheader("검증 계획·데이터 출처")
    st.markdown("""
- Persona 분류: 안전·생산·정비 전문가 라벨과 Macro-F1, Precision/Recall, 근거 키워드 적합성
- 사고 포커스: KOSHA 사례 전문가 다중라벨과 Macro-F1, 위험 태그 누락률
- 설비 위험: 정상운전·비사고 데이터 포함 PR-AUC, Recall, 오경보율, 치명위험 누락률
- 운영 효용: 야간 알림 건수, 중복경보 억제율, 확인시간, 조치 리드타임
    """)
    st.markdown("**데이터 출처**")
    st.write("• NVIDIA Nemotron-Personas-Korea: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea")
    st.write("• NVIDIA Nemotron-Personas-Korea-Extended: https://catalog.ngc.nvidia.com/orgs/nvidia/nemotron-personas/resources/nemotron-personas-dataset-ko_kr/-")
    st.write("• KOSHA 제조업 사고사례: https://www.data.go.kr/data/15163146/fileData.do")
    st.write("• 설비별 위험 경로 원본: https://github.com/ahky900-art/refractory/blob/main/ontology-enhanced.js")
    st.write("• 설비별 정비 위험 프로파일: https://github.com/ahky900-art/refractory/blob/main/maintenance-planning.js")
    st.warning("사고사례만으로 정상상태 대비 사고확률을 학습할 수 없습니다. PLC·센서·작업허가·LOTO·정상운전·비사고 이력, 현장 위험성평가 및 전문가 검증이 필요합니다.")
