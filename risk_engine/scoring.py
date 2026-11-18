from dataclasses import dataclass

@dataclass
class RiskResult:
    score: float
    level: str
    hard_alert: bool
    reasons: list[str]

def calculate_risk(severity: int, likelihood: int, exposure: int, control_effectiveness: float, loto_confirmed: bool = True, maintenance_active: bool = False) -> RiskResult:
    for name, value in [("severity", severity), ("likelihood", likelihood), ("exposure", exposure)]:
        if not 1 <= int(value) <= 5:
            raise ValueError(f"{name}는 1~5 범위여야 합니다.")
    if not 0 <= float(control_effectiveness) <= 1:
        raise ValueError("control_effectiveness는 0~1 범위여야 합니다.")
    score = 100 * (severity/5) * (likelihood/5) * (exposure/5) * (1-control_effectiveness)
    hard_alert = bool(maintenance_active and not loto_confirmed)
    level = "긴급" if hard_alert or score >= 60 else "주의" if score >= 35 else "관찰" if score >= 15 else "낮음"
    reasons = []
    if hard_alert:
        reasons.append("정비 중 LOTO 미확인: 점수와 무관한 핵심 통제 실패")
    if score >= 60:
        reasons.append("데모 위험점수 60 이상")
    return RiskResult(round(score, 1), level, hard_alert, reasons)
