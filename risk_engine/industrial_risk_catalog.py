"""Evidence-labelled industrial risk catalogue adapted from ahky900-art/refractory.

The source ontology's causal chains are retained as qualitative, conditional pathways.
Signal candidates are engineering monitoring suggestions, not validated predictors.
"""
EQUIPMENT = {
 "ladle":"래들",
 "kiln":"로타리 킬른",
 "rfcc":"RFCC 재생기",
 "inc":"소각로",
 "inc_melt":"용융로형 소각로",
 "inc_grate":"화격자형 소각로",
 "rh":"가열로",
 "bf":"고로",
 "sr":"2차 개질로",
 "ab":"Claus Thermal Reactor",
 "cfb":"CFB 보일러",
}

# Each path follows: operating/maintenance driver -> process state -> mechanism -> damage -> zone.
# "monitor" are proposed observable signals to investigate; they are not proof of damage.
PATHS = {
 "ladle":[
  {"driver":"슬래그 FeOx·SiO₂ 증가","change":"조성 증가/변화","state":"슬래그 점도·젖음성 변화 및 저융점 반응상 형성","mechanism":"MgO 용해·입계 침투·반응층 박리","damage":"슬래그 라인 용손·침투층 확대","zone":"슬래그 라인","condition":"슬래그 염기도, MgO 포화도, 온도·유동 조건과 함께 판단","evidence":"refractory/ontology-enhanced.js: feo; steel","monitor":["슬래그 XRF 조성","슬래그 라인 잔여 두께","벽면 온도·쉘 온도 추세"]},
  {"driver":"교반 가스 유량·교반 시간","change":"증가","state":"벽면 전단응력 및 슬래그/용강 물질전달 증가","mechanism":"침식·용해 경계층 제거","damage":"슬래그 라인 국부 침식 가속","zone":"슬래그 라인·용강 접촉 측벽","condition":"가스 유량뿐 아니라 플러그 위치·기포 패턴·교반 시간 포함","evidence":"refractory/ontology-enhanced.js: steel","monitor":["가스 유량·압력","교반 시간","국부 잔여 두께·침식 형상"]},
  {"driver":"출강 온도·고온 유지시간","change":"증가","state":"내화물-용강/슬래그 계면 반응속도 증가","mechanism":"화학적 용해·산화 및 침투 촉진","damage":"용손·잔존 두께 감소","zone":"용강 접촉 측벽·슬래그 라인","condition":"재질별 상평형·슬래그 조성과 함께 해석","evidence":"refractory/ontology-enhanced.js: feo","monitor":["출강·대기 온도 이력","고온 유지시간","잔여 두께 측정"]},
  {"driver":"래들 대기·냉각 시간 및 재가열 속도","change":"급격한 변화·반복 증가","state":"내화물 내외부 온도 구배와 열팽창 차이 증가","mechanism":"열피로·열충격","damage":"균열·스폴링·벽돌 탈락","zone":"용강 접촉 측벽·바닥","condition":"현재 래들 열모델은 열충격 박락을 직접 계산하지 않음","evidence":"refractory/ontology-enhanced.js: ladle","monitor":["대기시간·온도 램프","열화상 온도 분포","균열·박락 검사 기록"]}
 ],
 "kiln":[
  {"driver":"슬러지·원료의 Fe/알칼리/염류 및 회분 조성","change":"용융상 형성 가능 성분 증가","state":"저융점 액상·점착성 용융물 생성","mechanism":"액상 침투·용해·클링커 부착","damage":"벽돌 침식·코팅/링 형성 악화","zone":"소성대·전이대","condition":"원료 XRF/회분 융점·점도 및 킬른 온도 동시 확인. 코팅은 보호 기능도 있어 항상 손상 증가로 단정 금지","evidence":"refractory/ontology-enhanced.js: kiln","monitor":["원료·회분 XRF 및 융점","소성대 온도","링·코팅 변화","벽돌 잔여 두께"]},
  {"driver":"원료 처리량·가스 유속·분진 부하","change":"증가","state":"고체 입자 충돌 빈도와 벽면 전단 증가","mechanism":"마모·침식","damage":"입구/예열대 라이닝 두께 감소","zone":"입구/예열대","condition":"입도·분진량·유속·벽면 각도에 따라 영향 변화","evidence":"refractory/ontology-enhanced.js: kiln","monitor":["원료 처리량","가스 유속·차압","분진량·입도","입구 라이닝 두께"]},
  {"driver":"소성 온도·고온 체류시간","change":"증가","state":"클링커 액상량 및 벽돌 계면 반응 증가","mechanism":"열화학적 용손·침투","damage":"소성대 용손·코팅 불안정","zone":"소성대","condition":"코팅은 보호 기능도 있으므로 액상량 증가를 손상과 동일시하지 않음","evidence":"refractory/ontology-enhanced.js: kiln","monitor":["소성 온도·체류시간","쉘 스캐너 핫스팟","코팅·링 추세","잔여 두께"]},
  {"driver":"기동·정지 횟수 및 승강온 속도","change":"급격한 변화·반복 증가","state":"벽돌·쉘·코팅 사이 열팽창 차이 증가","mechanism":"열피로·코팅 박리","damage":"전이대 균열·스폴링","zone":"상부/하부 전이대","condition":"쉘 온도·정지 이력·벽돌 종류 결합","evidence":"refractory/ontology-enhanced.js: kiln","monitor":["기동·정지 횟수","승강온 속도","쉘 온도 추세","전이대 검사 이력"]}
 ],
 "rfcc":[
  {"driver":"촉매 순환량·입자 속도·분진 농도","change":"증가","state":"고체 입자 충돌 운동량·벽면 전단 증가","mechanism":"고속 입자 침식","damage":"캐스터블 라이닝 국부 두께 감소","zone":"사이클론·전이 콘·덴스 베드","condition":"입자 속도는 침식에 비선형 영향을 주므로 유량만으로 추정하지 않음","evidence":"refractory/ontology-enhanced.js: steel","monitor":["촉매 순환량·입도","사이클론 차압","촉매 손실량","라이닝 두께·국부 마모"]},
  {"driver":"재생기 후연소·국부 O₂·온도","change":"증가","state":"희박상/사이클론 국부 과열 및 산화 분위기 강화","mechanism":"소결·산화·열화학적 균열","damage":"핫스팟·균열·박락","zone":"희박상·사이클론 상부","condition":"O₂, CO, 온도 분포, 촉매 후연소 위치 확인","evidence":"refractory/ontology-enhanced.js: sic","monitor":["O₂·CO","다점 온도·쉘 온도","후연소 위치","핫스팟 추세"]},
  {"driver":"촉매 입도·응집·유동 편류","change":"편류·응집 증가","state":"특정 벽면 충돌과 마찰 집중","mechanism":"국부 침식·마모","damage":"타깃벽·접선부 편중 마모","zone":"사이클론 접선부·타깃벽","condition":"차압·촉매 손실·분배기 상태는 보조 지표","evidence":"refractory/ontology-enhanced.js: steel","monitor":["사이클론 차압","촉매 손실·입도","온도 비대칭","검사 위치별 마모"]},
  {"driver":"앵커·헥스메시 부식/간격·캐스터블 두께","change":"열화·불균일 증가","state":"라이닝 지지력 저하 및 열팽창 구속 변화","mechanism":"앵커 파손·박리","damage":"대면적 라이닝 탈락","zone":"전이 콘·희박상","condition":"앵커 재질·용접·간격과 시공 로트 확인","evidence":"refractory/ontology-enhanced.js: sic","monitor":["앵커 검사·NDT","쉘 온도","라이닝 두께·시공기록"]}
 ],
 "inc":[
  {"driver":"폐기물 내 Na/K/Cl/S 및 회분 조성","change":"증가","state":"알칼리염·황산염·염화물 함유 침착물/저융점 액상 형성","mechanism":"용융염 부식·기공 침투·반응층 형성","damage":"화학적 용손·표면 박리","zone":"연소실·2차 연소실","condition":"폐기물 성상과 비산회/바닥재 분석을 분리","evidence":"refractory/ontology-enhanced.js: sic","monitor":["폐기물·비산회·바닥재 XRF","연소실 온도","라이닝 표면·두께 검사"]},
  {"driver":"폐기물 발열량·수분·투입량 변동","change":"변동폭·빈도 증가","state":"연소온도와 열유속의 반복 변동","mechanism":"열피로·열충격","damage":"균열·스폴링·캐스터블 탈락","zone":"연소실·2차 연소실","condition":"수분·발열량·투입률과 온도 시계열 시간 정렬","evidence":"refractory/ontology-enhanced.js: incslag","monitor":["폐기물 수분·발열량","투입량 변동","온도 변동폭·램프","균열·박락 검사"]},
  {"driver":"회분·클링커의 유속·충돌·배출량","change":"증가","state":"벽면 충돌·마찰·전단 및 부착물 탈락","mechanism":"기계적 침식·마모","damage":"측벽·하부·배출부 마모","zone":"슬래그·회분 접촉부","condition":"회분 입도·경도·유속·충돌 각도 필요","evidence":"refractory/ontology-enhanced.js: kiln","monitor":["회분량·입도","배출부 차압·막힘","국부 두께·마모 형상"]},
  {"driver":"캐스터블 수분·두께·양생·드라이아웃 곡선","change":"수분/두께 증가 또는 승온 과속","state":"내부 증기압·온도 구배 증가","mechanism":"폭렬성 스폴링·건조 균열","damage":"초기 운전 중 대면적 박락","zone":"연소실·2차 연소실","condition":"제품·두께·시공법별 제조사 승인 건조 곡선 적용","evidence":"refractory/ontology-enhanced.js: incslag","monitor":["시공 수분·두께 기록","양생·드라이아웃 온도/시간 로그","열전대·쉘 온도","초기 운전 후 검사"]}
 ],
 "inc_melt":[
  {"driver":"슬래그 SiO₂·FeOx·알칼리·염기성 성분","change":"조성 변화","state":"슬래그 액상선·점도·젖음성 및 내화물 화학적 적합성 변화","mechanism":"용해·확산·침투·저융점 반응층 형성","damage":"용융조 벽·바닥 용손 및 침투층 확대","zone":"용융실·용융조","condition":"슬래그 조성 분석과 실제 온도 상평형/용융성 확인","evidence":"refractory/ontology-enhanced.js: feo; incslag","monitor":["슬래그 XRF·염기도","용융 온도","용융조 잔여 두께","쉘 온도·열화상"]},
  {"driver":"용융 온도·용융물 접촉시간","change":"증가","state":"계면 반응 및 용해 속도 증가","mechanism":"화학적 부식·용융 침식","damage":"슬래그 라인 후퇴·잔존 두께 감소","zone":"슬래그 라인","condition":"온도뿐 아니라 포화도·유속·산화환원 조건 반영","evidence":"refractory/ontology-enhanced.js: feo","monitor":["용융 온도·접촉시간","슬래그 조성","슬래그 라인 두께"]},
  {"driver":"출탕 유량·배출 속도·노즐 단면","change":"증가 또는 편류","state":"출탕구 국부 전단·마찰·온도 구배 증가","mechanism":"유동 침식·열기계적 마모","damage":"출탕구 확대·노즐 손상","zone":"출탕구·배출구","condition":"출탕 패턴·막힘 제거 작업 이력 포함","evidence":"refractory/ontology-enhanced.js: feo","monitor":["출탕 유량·시간","노즐 개구·마모","출탕 작업 이력","국부 온도"]},
  {"driver":"내화물 기공률·침투층/보호층 유지","change":"기공률 증가 또는 보호층 손실","state":"용융 슬래그와 반응 가능한 면적·침투 깊이 증가","mechanism":"침투 후 용해 및 구조 약화","damage":"용손 가속·국부 관통 위험","zone":"용융실·용융조","condition":"후시료 분석과 재질 적합성 시험으로 검증","evidence":"refractory/ontology-enhanced.js: feo","monitor":["시료 기공률·조직","침투층 깊이","두께 맵·쉘 온도"]}
 ],
 "inc_grate":[
  {"driver":"폐기물 내 Cl·Na/K·S 및 비산회 조성","change":"증가","state":"알칼리 염화물·황산염 침착과 고온 부식성 환경 강화","mechanism":"용융염 부식·침투·산화","damage":"내화물 표면 부식·박리 및 인접 금속부 스케일/입계 부식","zone":"화격자 상부 연소실·후연소실","condition":"2024 화격자 사례는 금속 그레이팅 손상 근거이며 내화물 손상과 구분","evidence":"refractory/ontology-enhanced.js: grate; sic","monitor":["폐기물·비산회 Cl/Na/K/S","연소실 온도","내화물 표면·두께","화격자 금속부 검사 별도"]},
  {"driver":"폐기물 투입량·낙하 높이·화격자 이동 속도","change":"증가","state":"폐기물/회분 충돌 에너지와 마찰 빈도 증가","mechanism":"충격·마모·침식","damage":"화격자 상부 및 하부 측벽 마모","zone":"화격자 상부 연소실·재 배출부","condition":"화격자 냉각형식·폐기물 층 두께·낙하 경로 반영","evidence":"refractory/ontology-enhanced.js: grate","monitor":["투입량·낙하 이벤트","화격자 속도","회분량·입도","상부 라이닝 두께"]},
  {"driver":"연소 공기 분배·국부 화염·온도 편차","change":"편차 증가","state":"국부 과열과 내화물 내외부 온도 구배 증가","mechanism":"열피로·열충격·산화","damage":"균열·박락·핫스팟","zone":"측벽·천장·후연소실","condition":"1차/2차 공기 분배와 화격자 냉각 데이터 결합","evidence":"refractory/ontology-enhanced.js: sic","monitor":["1차·2차 공기량","다점 온도 편차","열화상·쉘 온도","균열·박락 검사"]},
  {"driver":"SiC계 벽돌/캐스터블 결합계·산화·조인트","change":"산화/열화·조인트 개방 증가","state":"SiC 산화 및 염/알칼리 침투 경로 증가","mechanism":"산화·화학 부식·조인트 침식","damage":"표면 열화·균열·국부 탈락","zone":"화격자 상부·측벽","condition":"SiC 적용은 부위별 산화 분위기·수증기·염류 조건에 적합성 검토","evidence":"refractory/ontology-enhanced.js: sic","monitor":["SiC 표면·조인트 검사","수증기·온도·염류 조건","시료 분석·두께 맵"]}
 ],
 "rh":[
  {"driver":"버너 화염 길이·방향·공기비·연소 부하","change":"화염 충돌·편류 증가","state":"버너 포트/천장 국부 열유속 증가","mechanism":"국부 과열·열화학적 열화","damage":"버너 블록 균열·천장 핫스팟","zone":"버너 블록·가열대","condition":"화염 시야·노온 분포·버너 밸런스 함께 점검","evidence":"refractory/ontology-enhanced.js: steel","monitor":["버너별 부하·공기비","화염 방향·길이","노온 다점 편차","열화상·쉘 온도"]},
  {"driver":"강재 스케일 발생량·낙하·이송 빈도","change":"증가","state":"FeO계 스케일의 노상 접촉·마찰 증가","mechanism":"용융 스케일 침투·노상 마모","damage":"노상·스키드 주변 침식","zone":"노상·스키드 주변","condition":"강종·가열 온도·스케일 제거 주기 포함","evidence":"refractory/ontology-enhanced.js: feo","monitor":["강종·가열 온도","스케일 발생·제거량","노상 두께·스키드 주변 검사"]},
  {"driver":"장입/추출 주기·저부하 운전·재가열 횟수","change":"반복·변동 증가","state":"노벽·천장·노상 열사이클 누적","mechanism":"열피로·스폴링","damage":"천장·도어·버너 주변 박락","zone":"가열대·도어·전이부","condition":"온도 램프·정지시간·노내 위치별 온도 편차","evidence":"refractory/ontology-enhanced.js: steel","monitor":["기동·정지 횟수","승강온 속도","노내 위치별 온도","박락·균열 기록"]}
 ],
 "bf":[
  {"driver":"슬래그 FeO·SiO₂·알칼리 조성 및 용선 온도","change":"부식성 성분/온도 증가","state":"용선·슬래그와 카본/탄화규소계 내화물 계면 반응 증가","mechanism":"용해·침투·열화학적 부식","damage":"노상·출선구 잔존 두께 감소","zone":"노상·용선 접촉부·출선구","condition":"슬래그 포화도·냉각 열유속·용선 유동 포함","evidence":"refractory/ontology-enhanced.js: feo","monitor":["슬래그 조성·용선 온도","냉각수 열수지·열전대","노상 온도·열유속","출선구 검사"]},
  {"driver":"송풍량·가스 유속·장입물 낙하/하강","change":"증가","state":"가스·분진·장입물 벽면 충돌과 전단 증가","mechanism":"마모·침식","damage":"샤프트·보시 국부 마모","zone":"벨리·샤프트","condition":"입도 분포·가스 분배·장입 편류 확인","evidence":"refractory/ontology-enhanced.js: steel","monitor":["송풍량·가스 유속","장입물 입도·분배","벽체 온도·두께"]},
  {"driver":"출선 빈도·용선 유속·출선구 개공 조건","change":"증가 또는 편류","state":"출선구 주변 유동·마찰·열부하 집중","mechanism":"기계적 침식·용손","damage":"출선구 확대·주변 내화물 손상","zone":"출선구","condition":"개공 길이·머드건 재료·출선 패턴 함께 해석","evidence":"refractory/ontology-enhanced.js: feo","monitor":["출선 횟수·시간","개공 길이·머드건 사용량","출선구 직경·보수 이력"]},
  {"driver":"휴풍·감풍·재가동 및 냉각 이력","change":"급격한 변화·반복 증가","state":"노상/샤프트 온도 구배 및 구조 응력 변화","mechanism":"열충격·열피로","damage":"균열·박락·벽체 변형","zone":"노상·하부 샤프트","condition":"휴풍 기간과 냉각/재가열 속도 기록","evidence":"refractory/ontology-enhanced.js: steel","monitor":["휴풍·감풍 이벤트","온도 램프·냉각속도","열전대·쉘 변형"]}
 ],
 "sr":[
  {"driver":"공정가스/스팀 유량·조성·수증기 분압","change":"증가 또는 변동","state":"라이닝 표면 화학 분위기·열전달 변화","mechanism":"가스-고체 반응·휘발/재응축 가능성","damage":"표면 열화·균열·국부 핫스팟","zone":"연소실·출구 전이부","condition":"실제 개질가스 조성·온도·재질 상평형으로 검증","evidence":"refractory/ontology-enhanced.js: sic","monitor":["공정가스·스팀 조성/유량","수증기 분압","온도·쉘 핫스팟"]},
  {"driver":"버너 부하·화염 편향·출구 온도","change":"증가 또는 편류","state":"버너 주변 국부 과열·열유속 편차","mechanism":"열화학적 열화·열응력","damage":"버너 타일·돔 균열/박락","zone":"버너·연소실","condition":"버너별 부하·화염 방향·열전대 편차 확인","evidence":"refractory/ontology-enhanced.js: steel","monitor":["버너별 부하","화염 방향","출구 온도 편차","열화상"]},
  {"driver":"촉매 충전량·차압·가스 분배 편류","change":"증가 또는 편류","state":"촉매 지지부 하중·국부 유속·가스 우회 증가","mechanism":"기계적 응력·침식·핫스팟","damage":"촉매 지지 돔·전이부 손상","zone":"촉매 지지부·출구 전이부","condition":"차압 상승과 라이닝 온도/가스 우회 흔적 결합","evidence":"refractory/ontology-enhanced.js: steel","monitor":["촉매층 차압","가스 분배 편차","지지부 변형·온도"]}
 ],
 "ab":[
  {"driver":"H₂S/SO₂ 비율·공기비·황 증기·불순물","change":"조성/비율 변동","state":"연소실 산화환원 분위기와 황계 가스 분압 변화","mechanism":"황계 가스 반응·화학적 침식 가능성","damage":"버너 타일·주 연소실 표면 열화","zone":"버너 타일·주 연소실","condition":"황 회수 라이선서 운전창·내화물 재질과 함께 검증","evidence":"refractory/ontology-enhanced.js: sic","monitor":["H₂S/SO₂ 비율","공기비·O₂","연소실 온도","라이선서 운전 편차"]},
  {"driver":"버너 부하·화염 길이·화염 충돌","change":"충돌/국부 부하 증가","state":"전면 헤드·측벽 국부 열유속 증가","mechanism":"국부 과열·열응력","damage":"버너 타일 균열·주 연소실 박락","zone":"버너 타일·주 연소실","condition":"버너 정렬·화염 시야·온도 편차 확인","evidence":"refractory/ontology-enhanced.js: steel","monitor":["버너 부하·공기비","화염 시야·방향","다점 온도·쉘 온도"]},
  {"driver":"Checker brick 통로 분진·황 침착·차압","change":"침착·차압 증가","state":"유효 개구율 감소와 가스 유동 편류","mechanism":"국부 유속 증가·열점·막힘","damage":"격자 모서리 파손·균열·국부 과열","zone":"Checker brick 격자","condition":"차압 추세와 실제 통로 개구율·침착물 분석 결합","evidence":"refractory/ontology-enhanced.js: sic","monitor":["Checker 차압","개구율·막힘 검사","출구 온도 편차","침착물 성상"]}
 ],
 "cfb":[
  {"driver":"순환재 유량·입자 속도·고형물 농도","change":"증가","state":"고속 입자 충돌 운동량·벽면 전단 증가","mechanism":"입자 침식·마모","damage":"사이클론 접선부·덕트 라이닝 두께 감소","zone":"사이클론 접선부·입구 덕트","condition":"입자 크기·속도·방향 및 라이닝 경도 확인","evidence":"refractory/ontology-enhanced.js: steel","monitor":["순환재 유량·입도","사이클론 차압","국부 쉘 온도","라이닝 두께"]},
  {"driver":"연료 회분의 Na/K/Cl/S 및 융점","change":"부식성 성분·저융점 분율 증가","state":"알칼리염·황산염 침착 및 액상 형성","mechanism":"화학적 부식·침투","damage":"베드·전이부 라이닝 용손","zone":"하부 노·내화물-수냉벽 전이부","condition":"회분 XRF·융점·운전 온도 비교","evidence":"refractory/ontology-enhanced.js: sic","monitor":["회분 XRF·융점","베드 온도","전이부 두께·쉘 온도"]},
  {"driver":"베드 온도·국부 후연소·공기 분배","change":"편차·과열 증가","state":"국부 고온·산화 분위기 및 열유속 집중","mechanism":"열화학적 열화·열응력","damage":"핫스팟·균열·박락","zone":"하부 노·사이클론","condition":"온도·O₂·CO·차압의 공간 편차 분석","evidence":"refractory/ontology-enhanced.js: sic","monitor":["다점 온도·O₂·CO","차압·공기 분배","열화상·쉘 온도"]},
  {"driver":"앵커·스터드·용접·캐스터블 수분/건조","change":"열화·불균일 증가","state":"지지력 저하·증기압·국부 응력 집중","mechanism":"박리·폭렬성 스폴링","damage":"대면적 라이닝 탈락","zone":"전이부·루프실·딥레그","condition":"앵커 검사와 제조사 승인 dry-out 곡선을 필수 연결","evidence":"refractory/ontology-enhanced.js: steel; sic","monitor":["앵커·용접 검사","캐스터블 수분·두께","dry-out 온도/시간 로그"]}
 ]
}

# Separate occupational-safety triggers. They are task/control checks, not predictions from synthetic persona traits.
WORK_SAFETY = [
 {"task":"회전설비 정비·이물 제거","hazard":"끼임·말림","triggers":["설비 운전상태 불명","LOTO 미확인","방호장치 해제","위험구역 접근"],"controls":["정지·에너지 격리 확인","LOTO 잠금·표찰 교차확인","무전압/무압력 등 잔류에너지 확인","방호장치 복구·시운전 승인"],"hard_alert":"정비 중 LOTO 미확인"},
 {"task":"크레인·호이스트 인양","hazard":"낙하물·협착·충돌","triggers":["인양물 하부 작업자","슬링·샤클 손상/정격 미확인","신호수 부재","동선 교차"],"controls":["인양구역 출입통제","정격·체결상태 점검","신호수·운전원 통신","매달린 하중 하부 접근 금지"],"hard_alert":"매달린 하중 아래 사람 감지"},
 {"task":"고소·개구부 주변 작업","hazard":"추락","triggers":["난간·덮개 미설치","추락방호 미착용","작업발판 불량","기상·조도 불량"],"controls":["개구부 덮개·난간","작업발판·비계 점검","추락방호체계 확인","작업허가·감독"],"hard_alert":"개구부 방호 미확보 상태의 작업자 접근"},
 {"task":"용융물·고온 설비 주변 작업","hazard":"화상·용융물 접촉","triggers":["용융물 누출/비산","고온 표면 접근","냉각·차폐 이상","PPE 미확인"],"controls":["용융물 경로·비상대피구역 확보","차폐·냉각계 확인","내열 PPE","작업 전 온도·잔류물 확인"],"hard_alert":"용융물 누출 또는 비산 감지"},
 {"task":"밀폐공간·덕트·호퍼 내부 작업","hazard":"산소결핍·유해가스·매몰","triggers":["가스측정 미실시","환기 중단","격리 미흡","감시인·구조계획 부재"],"controls":["산소·유해가스 측정","환기·에너지 격리","감시인·통신","구조장비·구조계획"],"hard_alert":"가스측정 미확인 또는 산소/유해가스 경보"},
 {"task":"지게차·로더·운반차량 운행","hazard":"충돌·끼임","triggers":["보행자·차량 동선 중첩","후진 사각","속도·시야 제한","유도자 부재"],"controls":["보행자/차량 동선 분리","속도·후진 경보","유도자·교차로 시야 확보","운행 전 점검"],"hard_alert":"보행자-차량 위험구역 동시 점유"}
]
