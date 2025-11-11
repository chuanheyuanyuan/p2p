from typing import Literal

Decision = Literal['APPROVE', 'REVIEW', 'REJECT']


def evaluate(user_id: str, loan_id: str, amount: float) -> tuple[Decision, int]:
    # stub: simple rule
    if amount > 1200:
        return 'REVIEW', 580
    return 'APPROVE', 720
