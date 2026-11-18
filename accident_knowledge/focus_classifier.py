"""Transparent keyword tagging of accident narrative fields; not probability prediction."""
RULES={
 "끼임·말림·협착":["끼임","말림","협착","회전부","롤러","롤","기어","컨베이어","끼어"],
 "추락·전도":["추락","떨어짐","전도","넘어짐","개구부","사다리","비계","고소"],
 "충돌·낙하물":["충돌","부딪힘","맞음","낙하","비래","크레인","지게차","인양","운반"],
 "화재·폭발·화상":["화재","폭발","화상","화염","용융","고온","불티","가스누출","점화"],
 "질식·중독·유해물질":["질식","산소결핍","중독","유해가스","밀폐공간","황화수소","일산화탄소","분진","누출"],
 "감전·전기·에너지":["감전","전기","누전","아크","전원","정전","차단기","에너지 차단"],
 "근골격·수작업":["근골격","중량물","근육","요통","반복작업","수작업","인력운반"]
}
QUESTIONS={
 "끼임·말림·협착":["회전·왕복부가 정지됐는가?","방호덮개·인터록이 유효한가?","정비·이물 제거 전 LOTO가 확인됐는가?"],
 "추락·전도":["난간·덮개·작업발판이 확보됐는가?","추락방호체계와 안전대 체결점이 확인됐는가?"],
 "충돌·낙하물":["보행자와 차량·하중 동선이 분리됐는가?","인양구역 통제와 신호수가 있는가?"],
 "화재·폭발·화상":["가연성 가스·분진·증기 농도가 관리되는가?","점화원 통제·차폐·비상대피가 준비됐는가?"],
 "질식·중독·유해물질":["작업 전·중 산소·유해가스 측정이 이뤄졌는가?","환기·격리·감시인·구조계획이 있는가?"],
 "감전·전기·에너지":["전원 차단·검전·접지가 확인됐는가?","잔류·저장 에너지가 제거됐는가?"],
 "근골격·수작업":["중량·빈도·자세·운반거리가 평가됐는가?","기계화·보조구·2인 작업이 검토됐는가?"]
}
def classify_accident_focus(record):
    fields=["title","description","cause","prevention"]
    text=" ".join(str(record.get(k,"") or "") for k in fields).lower()
    hits=[]
    for label,words in RULES.items():
        matched=[w for w in words if w.lower() in text]
        if matched: hits.append({"label":label,"matched_terms":matched,"questions":QUESTIONS[label],"score":len(matched)})
    hits.sort(key=lambda x:x["score"],reverse=True)
    return {"primary":hits[0]["label"] if hits else "미분류","hits":hits,"source_fields":fields,"method":"keyword_multi_label_case_tagging"}
