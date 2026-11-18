from persona_engine.classifier import classify_ocean
from risk_engine.scoring import calculate_risk

def test_ocean_role():
    result = classify_ocean({"openness":0.9,"conscientiousness":0.8,"extraversion":0.2,"agreeableness":0.4,"neuroticism":0.3})
    assert result["role"] in {"Analytical","Procedural","Situational","Control"}

def test_hard_alert_overrides_score():
    result = calculate_risk(1,1,1,0.9,loto_confirmed=False,maintenance_active=True)
    assert result.hard_alert
    assert result.level == "긴급"

def test_score_range():
    result = calculate_risk(5,5,5,0.0)
    assert result.score == 100
