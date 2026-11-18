"""Explainable work-function taxonomy for synthetic persona records."""
ROLE_DEFINITIONS = {
 "process_materials":{"label":"공정·원료·재료 분석","focus":"원료 성상·조성·반응성·열/물질수지","incident_lens":"원료·공정 편차 → 이상상태·열화","keywords":["공정","화학","재료","금속","야금","원료","광물","슬래그","회분","소재","열역학","반응","제련","소성","process","chemical","materials","metallurgy","raw material"],"questions":["원료·연료·슬래그 조성이나 입도 변화가 있었는가?","온도·유량·압력·체류시간 변화가 손상 메커니즘과 일치하는가?"]},
 "equipment_maintenance":{"label":"설비·기계·정비","focus":"회전·구동부·압력·유체설비·진동·정비상태","incident_lens":"설비 고장·방호 실패·에너지 격리 미흡","keywords":["기계","설비","정비","보전","회전","펌프","밸브","베어링","기어","용접","배관","압력용기","크레인","지게차","maintenance","mechanical","equipment","rotating","pump","valve"],"questions":["설비 정지와 잔류에너지 격리가 확인됐는가?","진동·온도·차압·누설·마모 추세가 평소와 달라졌는가?"]},
 "electrical_control":{"label":"전기·계장·자동화","focus":"전기 에너지·PLC·인터록·센서·계측 신뢰도","incident_lens":"인터록 우회·센서 오류·감전·아크 위험","keywords":["전기","계장","자동화","제어","PLC","센서","계측","인터록","전력","모터","instrument","electrical","automation","control","sensor"],"questions":["인터록·비상정지·경보가 정상 동작하는가?","센서 결측·고정값·드리프트가 발생했는가?"]},
 "production_operations":{"label":"생산·운전","focus":"운전조건·생산량·부하·기동정지·작업순서","incident_lens":"운전 편차·절차 이탈·비정상 운전 위험","keywords":["생산","운전","조업","오퍼레이터","운전원","현장운전","용해","소각","보일러","킬른","가열로","production","operator","operation","furnace","kiln"],"questions":["부하·온도·유량·압력·조업시간이 운전창을 벗어났는가?","작업순서·운전모드·교대 인수인계가 변경됐는가?"]},
 "safety_environment":{"label":"안전·환경·보건","focus":"위험성평가·작업허가·LOTO·밀폐공간·화학물질","incident_lens":"추락·끼임·질식·화재·폭발·유해물질 노출","keywords":["안전","산업안전","보건","환경","위험성평가","작업허가","LOTO","밀폐공간","소방","환경관리","safety","environment","health","risk assessment"],"questions":["작업허가·위험성평가·LOTO·가스측정이 유효한가?","작업자와 위험구역·차량·용융물 경로가 겹치는가?"]},
 "logistics_lifting":{"label":"물류·운송·인양","focus":"지게차·크레인·운반·하역·적재·중량물","incident_lens":"충돌·협착·낙하물·전도 위험","keywords":["물류","운송","운반","하역","인양","크레인","호이스트","지게차","적재","창고","logistics","lifting","forklift","crane","transport"],"questions":["보행자와 차량·인양물 동선이 분리됐는가?","정격하중·슬링·샤클·신호수가 확인됐는가?"]},
 "quality_inspection":{"label":"품질·검사·분석","focus":"검사·시험·측정·NDT·품질편차","incident_lens":"결함 조기발견 실패·검사 누락·측정오류","keywords":["품질","검사","시험","분석","측정","비파괴","NDT","품질관리","실험실","laboratory","quality","inspection","testing"],"questions":["검사 데이터의 위치·시간·단위·교정상태가 일치하는가?","두께·균열·온도·진동 추세에서 이상점이 있는가?"]},
 "supervision_management":{"label":"관리·감독·인력운영","focus":"작업조정·인력·교대·동시작업·도급·구역통제","incident_lens":"감독 공백·작업 간섭·의사소통·허가 누락","keywords":["관리자","감독","팀장","공장장","생산관리","현장관리","공사관리","프로젝트관리","인사","교육","supervisor","manager","management","project"],"questions":["작업책임자·감시인·신호수가 지정됐는가?","동시작업과 도급작업 간 위험정보가 공유됐는가?"]}
}
FIELD_WEIGHTS={"occupation":4,"professional_persona":4,"skills_and_expertise_list":3,"skills_and_expertise":2,"detailed_persona":2,"career_goals_and_ambitions":1,"persona":1}
EXCLUDED_FIELDS=["sports_persona","arts_persona","travel_persona","culinary_persona","family_persona","finance_persona","healthcare_persona","hobbies_and_interests","cultural_background","sex","age","health","income","province","district","country","OCEAN"]

def classify_work_persona(record):
    scores={key:0 for key in ROLE_DEFINITIONS}; evidence={key:[] for key in ROLE_DEFINITIONS}; used=[]
    for field,weight in FIELD_WEIGHTS.items():
        raw=record.get(field,"")
        if raw is None: continue
        if isinstance(raw,(list,tuple,set)): raw=" ".join(map(str,raw))
        value=str(raw).lower()
        if not value.strip(): continue
        used.append(field)
        for role,definition in ROLE_DEFINITIONS.items():
            for word in definition["keywords"]:
                if word.lower() in value:
                    scores[role]+=weight
                    evidence[role].append({"field":field,"keyword":word,"weight":weight})
    ranked=sorted((k for k,v in scores.items() if v>0),key=lambda k:scores[k],reverse=True)
    total=sum(scores.values())
    return {"primary":ranked[0] if ranked else "unclassified",
      "ranked":[{"role":k,"label":ROLE_DEFINITIONS[k]["label"],"score":scores[k],"share":round(scores[k]/total,3),"focus":ROLE_DEFINITIONS[k]["focus"],"incident_lens":ROLE_DEFINITIONS[k]["incident_lens"],"questions":ROLE_DEFINITIONS[k]["questions"],"evidence":evidence[k]} for k in ranked],
      "scores":scores,"evidence":evidence,"used_fields":used,"excluded_fields":EXCLUDED_FIELDS}
