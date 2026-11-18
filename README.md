# Persona Manufacturing AI Safety Agent

합성 페르소나의 직무·전문성 맥락을 제조업 위험 검토 관점으로 연결하고, KOSHA 사고사례와 refractory 설비별 손상 온톨로지를 이용해 현장 위험 경로와 관측 후보를 제시하는 연구용 MVP입니다.

> **안전 고지:** Persona는 검토 관점을 제안할 뿐 근로자 개인의 성격·숙련도·사고확률을 예측하지 않습니다. 위험 경로와 관측 신호는 현장 검증 전 가설이며 실제 안전 감시나 법정 위험성평가를 대체하지 않습니다.

## 웹 대시보드 (GitHub Pages)\n\n정적 웹 대시보드: [Persona Manufacturing AI Safety Agent](https://ahky900-art.github.io/persona-manufacturing-ai-agent/)\n\nGitHub 저장소의 `docs/index.html`이 Pages용 화면이며, Streamlit Python 앱과는 별도입니다. Pages 배포를 처음 활성화할 때 저장소 Settings → Pages → Build and deployment → Source에서 **GitHub Actions**를 선택하십시오.\n\n## 로컬 Streamlit 대시보드 실행

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## 대시보드 탭

1. 전체 구조: Persona → 사고 포커스 → 설비 위험경로 → 관측 후보
2. Persona 분류 기준: Hugging Face 데이터 필드, 가중치, 역할별 키워드와 분류 근거
3. 사고 포커스: KOSHA 제목·개요·원인·예방대책에서 위험 태그 다중 추출
4. 산업현장 Risk: refractory 저장소의 11개 설비 유형별 인자→상태→메커니즘→손상→취약부위 경로
5. 작업자 안전 Risk: 끼임·추락·충돌·화재·질식·감전 등 인명 위험과 핵심 통제 체크
6. 온톨로지 경로: 선택한 설비·위험 경로를 그래프로 표시
7. 검증·출처: 모델 한계, 평가계획, 데이터 출처

## 1. Hugging Face Persona 분류 기준

기본 Nemotron-Personas-Korea는 26개 필드로 구성되고 OCEAN 점수는 기본 스키마에 포함되지 않습니다. NVIDIA Nemotron-Personas-Korea-Extended 설명은 51개 필드와 OCEAN 5개 문자열 속성을 제시합니다.

분류는 직무 관련 필드만 사용합니다.
- occupation: 가중치 4
- professional_persona: 가중치 4
- skills_and_expertise_list: 가중치 3
- skills_and_expertise: 가중치 2
- detailed_persona: 가중치 2
- career_goals_and_ambitions: 가중치 1
- persona: 가중치 1

필드별 일치 키워드와 가중치를 합산해 공정·원료·재료, 설비·정비, 전기·계장, 생산·운전, 안전·환경, 물류·인양, 품질·검사, 관리·감독 역할을 다중 분류합니다. 결과에는 매칭된 필드와 키워드가 표시됩니다.

OCEAN, MBTI, 성별, 연령, 건강, 가족, 소득, 지역 정보는 안전 역할 분류 및 위험점수에 사용하지 않습니다. 스포츠·예술·여행·요리 등 비직무 페르소나 필드도 직무 분류에서 제외합니다.

## 2. 사고 포커스

KOSHA 제조업 사고사례 CSV의 원본 컬럼을 다음과 같이 정규화합니다.
- BBSCTT_SJ_NM: 사고 제목
- BBSCTT_CN: 사고 발생 개요
- DSSTR_INDUCT_FCTR_CN: 사고 발생 원인
- RSKNSS_DCRS_CNTRPLN_CN: 재해예방 대책

텍스트에서 끼임·협착, 추락, 충돌·낙하물, 화재·폭발·화상, 질식·중독, 감전·전기, 근골격·수작업 태그를 다중 추출합니다. 이는 사례 검색·검토용 규칙 기반 태깅이며 사고확률 추정이 아닙니다.

## 3. 산업설비 위험 카탈로그

`risk_engine/industrial_risk_catalog.py`는 `ahky900-art/refractory`의 `ontology-enhanced.js` 및 `maintenance-planning.js`를 바탕으로 다음 11개 설비의 위험경로를 구조화합니다.

래들, 로터리 킬른, RFCC 재생기, 소각로, 용융로형 소각로, 화격자형 소각로, 가열로, 고로, 2차 개질로, Claus Thermal Reactor, CFB 보일러.

경로 구조:
운전/정비 인자 → 공정 상태 변화 → 물리·화학 메커니즘 → 예상 손상 → 취약 부위 → 관측 신호 후보.

관측 신호는 실제 센서가 연결된 값이 아닙니다. 현장 계측·검사 데이터에서 가용성, 시간 선행성, 손상과의 연관성을 검증해야 합니다.

## 4. 설비 위험과 작업자 안전 위험 분리

설비 건전성 위험(용손·침식·균열·박락·쉘 핫스팟)과 인명 안전 위험(끼임·추락·충돌·화상·질식·감전)은 별도 평가합니다. 예를 들어 정비 중 LOTO 미확인은 복합 위험점수와 무관한 핵심 통제 경보 후보입니다. 두 위험 점수를 임의로 합산하지 않습니다.

## 5. 데이터 출처

- NVIDIA base: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea
- NVIDIA Extended: https://catalog.ngc.nvidia.com/orgs/nvidia/nemotron-personas/resources/nemotron-personas-dataset-ko_kr/-
- KOSHA 실제 산업재해 사례(업무상 사고사례) OpenAPI: https://www.data.go.kr/data/15163146/fileData.do\n  - ODCloud Base URL: `https://api.odcloud.kr/api`\n  - Swagger: `https://infuser.odcloud.kr/oas/docs?namespace=15163146/v1`\n  - Dataset API path: `/15163146/v1/uddi:3c9aaf7a-965f-4531-9f31-d1049e13e115`\n  - 인증키는 `KOSHA_SERVICE_KEY` 환경변수로만 관리하고, 요청주소는 `KOSHA_API_URL`로 덮어쓸 수 있습니다.\n  - 기본 조회는 `page=1`, `perPage=100`; 추가 요청변수는 `KOSHA_API_PARAMS_JSON`에 JSON 객체로 지정합니다.
- 설비 위험 온톨로지: https://github.com/ahky900-art/refractory/blob/main/ontology-enhanced.js
- 설비 정비 프로파일: https://github.com/ahky900-art/refractory/blob/main/maintenance-planning.js

## 6. 검증상 한계

- 합성 페르소나는 실제 작업자 행동·숙련도·성격 데이터가 아닙니다.
- 사고사례는 사고 후 기록이며 정상상태 분포나 발생확률을 제공하지 않습니다.
- 설비 메커니즘과 관측신호 연결은 검증 전 가설입니다.
- 정상 운전·비사고 이력, PLC·센서·작업허가·LOTO 데이터, 검사 결과, 현장 전문가 라벨이 필요합니다.
- 검증은 역할 분류 Macro-F1, 사고 태깅 Macro-F1, 위험탐지 PR-AUC/Recall/오경보율, 치명위험 누락률, 관리자 응답시간으로 수행합니다.
- 실제 운영 전 산업안전 전문가 검토, 사업장 위험성평가 기준 보정, 인증·권한·감사로그가 필요합니다.

## 라이선스 및 출처 준수

각 데이터셋·공공데이터의 현재 라이선스, 출처표시, 변경·재배포 조건을 확인하십시오. KOSHA 원본 데이터는 원문을 임의 변경하지 말고, 분석용 정규화 결과를 별도 파생 데이터로 관리하십시오.
