# 온톨로지 노드·엣지 근거 레지스터

- 기준일: 2026-11-20
- 상태: 외부 문헌·법령 기반 초기 근거 등록 / 사업장별 검증 전
- 적용: `docs/index.html`, `persona_engine/role_taxonomy.py`, `accident_knowledge/focus_classifier.py`, `risk_engine/*`
- 원칙: 이 문서는 그래프의 의미·근거·한계를 정의한다. 근거가 있다는 이유만으로 인과관계나 현장 임계값이 검증되었다고 간주하지 않는다.

## 1. 설계 원칙

1. **원천 사실과 분석용 분류를 분리한다.** KOSHA 사고 원문의 제목·개요·원인·재해형태·작업·설비 필드는 원형 그대로 보존한다. 7개 사고 포커스는 검색·분석을 위한 파생 태그이며 공식 재해형태 분류를 대체하지 않는다.
2. **Persona는 사람의 사고성향이 아니다.** Hugging Face 합성 페르소나의 직무·전문성 필드에서 만든 8개 기능적 검토 관점이다. 개인별 사고확률, 성격, 숙련도, 안전행동을 추론하지 않는다.
3. **관계의 의미를 제한한다.** Persona와 사고유형은 `REVIEW_LENS_FOR`(검토 관점)로 연결한다. `CAUSES` 또는 `PREDICTS` 관계를 사용하지 않는다. 사고사례-설비 관계도 원문에 설비가 명시되었는지, 키워드만 일치했는지를 구분한다.
4. **다대다를 허용하되 모든 관계에 근거를 요구한다.** 엣지에는 출처, 원문 레코드, 근거 문장/필드, 적용 조건, 검토상태를 기록한다.
5. **Threshold의 출처 유형을 분리한다.** 법령 기준, 설비 제조사/설계 기준, 사업장 운전한계, 통계적 이상탐지 기준은 서로 다른 레코드다. 출처와 적용 범위가 확인되지 않은 수치는 운영 경보에 사용하지 않는다.
6. **설비 건전성과 인명안전을 분리한다.** 내화물 손상(용손·침식·열충격·박락)과 작업자 재해(끼임·추락·질식 등)는 별도 위험 경로와 경보 정책을 가진다.

## 2. 노드 분류와 생성 근거

| 노드 클래스 | 생성 근거 | 현재 상태 / 주의 |
|---|---|---|
| PersonaRole | Nemotron-Personas-Korea의 occupation, professional_persona, skills_and_expertise_list 등 직무 필드 | 8개는 프로젝트 내부 기능 분류. 외부 표준 분류가 아님 |
| AccidentRecord | KOSHA 업무상 사고사례 원천 레코드 | 원본 ID·원본 필드 보존 |
| OfficialAccidentType | KOSHA 원천 데이터의 재해형태 등 공식 제공 필드 | 코드·명칭은 원천 스키마에서 그대로 가져오며 임의 생성 금지 |
| AnalyticalHazardTag | 사고 제목·개요·원인·예방대책에서 키워드/문맥 추출 | 기존 7개 태그는 파생 분류이며 복수 태그 허용 |
| WorkActivity | 사고 원문 또는 작업허가서에 명시된 작업 | 텍스트 추출 결과는 근거 문장과 함께 보관 |
| Equipment / EquipmentPart | KOSHA 원문, 설비 마스터, P&ID/도면, 정비 프로파일 | 단순 키워드 일치만으로 실제 사고 설비 확정 금지 |
| HazardousCondition | 법령, 위험성평가, 사고조사, 작업절차 | 예: 회전부 노출, 에너지 격리 미확인, 산소결핍 |
| DamageMechanism | 동료심사 논문·기술 문헌·재료 분석 | 화학부식, 침투, 용손, 마모, 열피로 등 |
| DamageMode | 검사·정비·고장 분석 기록 및 문헌 | 균열, 스폴링, 박락, 두께감소 등 |
| ObservableSignal | 센서 사양서, 설비 설계, 검사기록, 문헌 | 계측 가능성과 손상 선행성을 검증해야 함 |
| Threshold | 법령/고시, 제조사 매뉴얼, 설계 기준, 승인된 운전 기준, 검증된 통계모델 | 출처·단위·설비·위치·버전 없는 값은 미설정 |
| Alert / ControlAction | 법령상 의무, 사업장 절차, 승인된 대응계획 | 자동 경보와 법정 조치의 차이를 명시 |

## 3. 8개 Persona 역할의 근거와 한계

현재 8개 역할은 다음 7개 직무 관련 필드의 가중 키워드 합산으로 분류한다: occupation(4), professional_persona(4), skills_and_expertise_list(3), skills_and_expertise(2), detailed_persona(2), career_goals_and_ambitions(1), persona(1).

이 가중치는 프로젝트의 초기 휴리스틱이며 통계적 학습·전문가 합의·예측성능으로 최적화된 값이 아니다. 역할은 중복 배정될 수 있고, 점수는 확률이 아니다.

| 역할 | 분류 근거(직무·기술 단서) | 연결의 올바른 의미 |
|---|---|---|
| 공정·원료·재료 | 공정, 화학, 재료, 금속, 야금, 원료, 광물, 슬래그, 회분 | 원료·공정 조건을 검토하는 관점 |
| 설비·기계·정비 | 기계, 설비, 정비, 회전, 펌프, 밸브, 베어링, 크레인 | 기계적 위험·정비·에너지 격리를 검토 |
| 전기·계장·자동화 | 전기, 계장, PLC, 센서, 인터록, 자동화 | 전기 위험·제어·계측 신뢰성을 검토 |
| 생산·운전 | 생산, 운전, 조업, 소각, 보일러, 킬른, 가열로 | 운전모드·공정조건·작업순서를 검토 |
| 안전·환경·보건 | 안전, 위험성평가, 작업허가, LOTO, 밀폐공간 | 법정·절차적 통제와 노출을 검토 |
| 물류·운송·인양 | 운반, 하역, 인양, 크레인, 호이스트, 지게차 | 차량·하중·보행자 동선을 검토 |
| 품질·검사·분석 | 품질, 검사, 시험, 측정, NDT, 분석 | 검사·측정·결함 검출 관점을 제공 |
| 관리·감독·인력운영 | 관리자, 감독, 교대, 프로젝트, 인력, 동시작업 | 작업조정·감독·도급 인터페이스를 검토 |

**금지:** PersonaRole → AccidentType의 인과 엣지. 허용: PersonaRole → `REVIEW_LENS_FOR` → Hazard/AccidentType. 이 엣지는 직무 필드와 역할 사전의 키워드 근거를 보유하며, 안전 전문가가 승인하기 전에는 '제안' 상태다.

## 4. 산재유형 체계

### 4.1 원천 분류

KOSHA 공공데이터포털의 '산업재해 사례(업무상 사고사례)' 설명에는 사고 제목, 발생 상황·과정, 재해 원인, 재해 형태, 작업·설비 관련 위험요인, 예방·재발방지 대책이 포함된다고 안내되어 있다. 실제 API/파일의 최신 컬럼 정의서와 코드값을 기준으로 원천 필드를 매핑한다. 현재 프로젝트의 7개 포커스 태그를 공식 분류로 표시하지 않는다.

### 4.2 분석용 7개 태그

- 끼임·말림·협착
- 추락·전도
- 충돌·낙하물
- 화재·폭발·화상
- 질식·중독·유해물질
- 감전·전기·에너지
- 근골격·수작업

이 목록은 프로젝트의 분석 편의를 위한 상위 태그다. 한 사고에 여러 태그가 붙을 수 있다. 키워드 매칭만으로 대표 사고유형을 확정하지 말고, 원천 재해형태 코드가 있으면 이를 우선 보존한다. 키워드만으로 붙은 태그의 관계 상태는 `candidate`로 둔다.

## 5. 엣지 타입과 증거 요구사항

| 엣지 | 의미 | 필수 증거 |
|---|---|---|
| `DERIVED_FROM` | 노드가 원천 레코드에서 추출됨 | 데이터셋·레코드 ID·필드 |
| `HAS_OFFICIAL_TYPE` | 사고 레코드의 원천 재해형태 | 원천 코드·명칭·컬럼 |
| `TAGGED_AS` | 분석용 위험태그 부여 | 일치 문장·태그 사전 버전·검토상태 |
| `REVIEW_LENS_FOR` | Persona 역할이 검토할 위험 관점 | 역할 필드·키워드·직무 근거 |
| `OCCURS_DURING` | 사고가 특정 작업 중 발생 | 사고 원문에 작업 명시 |
| `INVOLVES_EQUIPMENT` | 사고에 설비가 관여 | 사고 원문/조사보고서의 설비 명시 |
| `HAS_HAZARD` | 작업/설비가 위험상태를 가짐 | 법령·위험성평가·사고조사 |
| `CAN_LEAD_TO` | 위험상태가 재해/손상으로 이어질 수 있음 | 법령·사고조사·문헌, 적용조건 |
| `DRIVES_MECHANISM` | 운전인자가 물리·화학 상태를 변화 | 공정원리·논문·운전 데이터 |
| `CAUSES_DAMAGE_MODE` | 메커니즘이 손상형태를 유발 | 동료심사 문헌·검사/파손 분석 |
| `OBSERVED_BY` | 상태/손상을 센서·검사로 관측 | 센서 사양·검사 방법·단위 |
| `GOVERNED_BY_THRESHOLD` | 관측값이 기준과 비교됨 | 기준 출처·적용범위·단위·버전 |
| `TRIGGERS_ALERT` | 조건 충족 시 경보 | 승인된 로직·지연/지속 조건·조치 |
| `MITIGATED_BY` | 통제/조치가 위험을 저감 | 법령·표준·사업장 절차 |

모든 엣지는 `evidence_id`, `source_id`, `source_record_id`(해당 시), `evidence_quote_or_field`, `valid_from`, `review_status`, `method`를 기록한다. `confidence`는 검증된 평가 방법이 있을 때만 수치화하고, 그렇지 않으면 null로 둔다.

## 6. 외부 근거를 반영한 대표 관계

### 6.1 회전부 정비 → 끼임 위험

- OSHA 29 CFR 1910.212(a)(1): 작업점, 물림점(ingoing nip points), 회전부 등 기계 위험으로부터 작업자를 보호하기 위한 방호를 요구한다.
- OSHA 29 CFR 1910.147: 정비·서비스 중 예기치 않은 기동 또는 저장에너지 방출로 인한 부상을 막기 위해 에너지 제어 프로그램, 격리, 잠금/표찰 및 검증 절차를 요구한다.
- 관계: `RotatingPart` → `HAS_HAZARD` → `Entanglement/NipPoint`; `MaintenanceActivity` + `EnergyIsolationUnverified` → `CAN_LEAD_TO` → `UnexpectedStart/StoredEnergyExposure` → `TRIGGERS_ALERT`.
- 경보 정책: 정비 작업 활성 상태에서 에너지 격리·무전압/무압력 확인이 미완료면 위험점수와 별개인 하드 인터록/작업허가 경보 후보. 실제 구현은 사업장 LOTO 절차 및 설비 안전회로와 검증해야 한다.

### 6.2 밀폐공간 → 산소결핍·유해가스 노출

국내 「산업안전보건기준에 관한 규칙」 제618조의 '적정공기' 정의:
- 산소 18% 이상 23.5% 미만
- 이산화탄소 1.5% 미만
- 일산화탄소 30 ppm 미만
- 황화수소 10 ppm 미만

이 값들은 법령 정의의 적정공기 경계로 기록한다. O2 <18%는 법령상 산소결핍 정의와 연결한다. 법령상 '적정공기' 경계를 모든 센서의 일반 경보 지연·대피·재진입 로직으로 임의 확대하지 않는다. 측정 위치, 교정, 측정 주기, 작업 전·중 측정, 환기·감시·구조계획은 관련 조문 전체와 사업장 절차를 함께 반영한다.

### 6.3 위험성평가

산업안전보건법 제36조와 2026-11-04 시행 고용노동부고시 제2026-73호 「사업장 위험성평가에 관한 지침」을 기준으로 한다. 위험성평가는 설비·원재료·가스·분진·작업행동 등의 유해·위험요인을 찾고, 위험성을 결정하고, 개선대책을 이행하는 사업장별 절차다. 따라서 데모의 15/35/60 점수 구간은 법정 기준이 아니며 운영 기준으로 표시하면 안 된다. 위험성 수용 기준은 사업장별 승인·기록이 필요하다.

### 6.4 내화물 손상 메커니즘

- 고로 노상: 산화, 알칼리 공격, CO 공격, 열응력, 용선·슬래그 유동에 의한 용해/침식이 문헌에 보고됨.
- 소각로: H2O/HCl/SO2 및 Na/K 염·침착물의 상호작용, 염화물/황산염 관련 부식, SiC 산화 등 복합 부식 메커니즘이 보고됨.
- 로터리 킬른: 기계적 마모, 화학적 공격, 열충격, 과열, 코팅 불안정, 벽돌 스폴링·압궤가 구역별로 기술됨.
- 이 문헌들은 해당 메커니즘 노드의 근거다. 모든 설비·내화물 재질·운전조건에서 같은 메커니즘이 우세하다는 뜻은 아니다. 설비 구역, 벽돌/캐스터블 조성, 슬래그·가스 조성, 온도·유속·운전 이력을 조건으로 둔다.

## 7. Threshold 레지스터 규칙

Threshold 레코드는 최소한 다음 필드를 가진다.

- `threshold_id`, `signal_id`, `equipment_id`, `location_or_zone`
- `limit_type`: `LEGAL` / `DESIGN` / `OEM` / `SITE_OPERATING` / `STATISTICAL`
- `operator`: `<`, `<=`, `>`, `>=`, `rate_of_change`, `composite`
- `value`, `unit`, `duration`, `sampling_interval`, `hysteresis`
- `source_id`, `source_clause_or_page`, `effective_date`, `approval_status`
- `response_action`, `reset_condition`

우선순위: 법적 요구사항 및 안전 필수조건 → OEM/설계 한계 → 승인된 사업장 운전한계 → 검증된 통계/ML 이상탐지. AI 이상탐지 결과는 법적 기준을 대체하거나 완화하지 않는다. 출처·단위·적용구역·승인상태가 없는 임계값은 `UNSET`이며 운영 알람을 발생시키지 않는다.

## 8. 엣지/노드 데이터 계약 예시

```json
{
  "edge_id": "EDGE-LOTO-001",
  "from": "maintenance_activity",
  "relation": "REQUIRES_ENERGY_ISOLATION",
  "to": "energy_isolation_verified",
  "source_id": "SRC-OSHA-1910-147",
  "source_record_id": null,
  "evidence_quote_or_field": "1910.147(c)(1), (d)(3)-(d)(6)",
  "condition": ["servicing_or_maintenance", "hazardous_energy_present"],
  "method": "regulatory_rule_mapping",
  "confidence": null,
  "review_status": "source_verified_site_review_pending",
  "valid_from": "2026-11-20"
}
```

`confidence: null`은 미검증을 의미한다. 규정이 명확하다는 이유로 현장 적용·센서 연결까지 검증된 것으로 간주하지 않는다.

## 9. 출처 레지스터

| ID | 출처 | 사용 범위 |
|---|---|---|
| SRC-KOSHA-ACCIDENT-20260903 | https://www.data.go.kr/data/15163146/fileData.do | 사고사례 원천 구조·재해형태·작업·설비·예방대책 |
| SRC-KOSHA-RISK-GUIDE-2026 | https://www.law.go.kr/admRulLsInfoP.do?admRulSeq=2100000288038 | 2026-11-04 시행 위험성평가 지침 |
| SRC-KOSHA-SAFETY-RULE-618 | https://www.law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1033350811 | 밀폐공간·적정공기 기준, 제618조 이하 |
| SRC-OSHA-1910-147 | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147 | 위험에너지 제어, LOTO |
| SRC-OSHA-1910-212 | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212 | 기계 방호·회전부·물림점 |
| SRC-BF-REFRACTORY-REVIEW-2022 | https://doi.org/10.1002/srin.202200266 | 고로 내화물 물리손상·화학부식·기계침식 |
| SRC-INCINERATOR-CORROSION-2024 | https://doi.org/10.1016/j.corsci.2024.111933 | 소각로 H2O/HCl/SO2·염 침착물 결합 부식 |
| SRC-ROTARY-KILN-THICKNESS-2026 | https://doi.org/10.1016/j.measurement.2026.121405 | 로터리 킬른 내부온도·라이닝 두께 데이터/모델 기반 추정 |
| SRC-BF-HEARTH-ISIJ-2016 | https://www.jstage.jst.go.jp/article/isijinternational/56/11/56_ISIJINT-2016-168/_html/-char/en | 고로 노상 산화·알칼리·CO·열응력·용선/슬래그 용해 |

## 10. 다음 구현 작업

1. KOSHA 최신 원천 컬럼 정의서에서 공식 재해형태 코드·명칭을 확인하고 원본을 보존한다.
2. 현재 7개 키워드 태그를 공식 재해형태에 대응시키되, 매핑 불명확·다중 의미는 검토대기 상태로 둔다.
3. 8개 Persona를 `REVIEW_LENS_FOR` 엣지로 전환하고, 인과관계처럼 보이는 연결을 제거한다.
4. 설비별 위험경로의 각 인자→상태→메커니즘→손상→관측신호 엣지에 문헌/설비자료/현장자료 근거를 연결한다.
5. UI에서 노드·엣지 선택 시 출처·원문근거·조건·검증상태를 표시한다.
6. 임계값 편집 화면에서 출처유형·단위·설비구역·적용일·승인상태를 필수화한다.

이 문서의 근거가 등록되었다는 사실과 그래프 전체가 검증되었다는 사실은 다르다. 현장 데이터와 전문가 승인이 없는 관계는 계속 후보/가설 상태로 표시한다.
