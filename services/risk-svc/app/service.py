from typing import List

from .schemas import EvaluationRequest, EvaluationResponse


class Rule:
    def __init__(self, name: str, weight: int, predicate):
        self.name = name
        self.weight = weight
        self.predicate = predicate

    def evaluate(self, payload: EvaluationRequest) -> int:
        return self.weight if self.predicate(payload) else 0


RULES = [
    Rule('KYC_APPROVED', 200, lambda req: (req.signals.kyc or {}).get('status') == 'APPROVED'),
    Rule('DEVICE_PRIVACY_CONSENT', 100, lambda req: (req.signals.device or {}).get('privacyConsent') is True),
    Rule('NO_OVERDUE', 150, lambda req: ((req.signals.history or {}).get('overdueDays', 0) == 0)),
    Rule('HIGH_AMOUNT_PENALTY', -100, lambda req: req.loan.amount > 1000),
]


class RiskService:
    def evaluate(self, payload: EvaluationRequest) -> EvaluationResponse:
        base = 500
        reasons: List[str] = []
        for rule in RULES:
            gain = rule.evaluate(payload)
            if gain <= 0:
                reasons.append(f"MISS_{rule.name}")
            base += gain
        decision = self._decision(base)
        if decision == 'REJECT':
            reasons.append('BASE_SCORE_LOW')
        return EvaluationResponse(decision=decision, score=max(min(base, 900), 300), reasons=reasons)

    def _decision(self, score: int) -> str:
        if score >= 700:
            return 'APPROVE'
        if score >= 550:
            return 'REVIEW'
        return 'REJECT'
