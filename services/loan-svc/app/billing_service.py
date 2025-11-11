from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fastapi import HTTPException, status

from .models import LoanApplication, RepaymentSchedule
from .repository import get_application
from .schedule_repository import get_schedule, save_schedule

MONEY_QUANT = Decimal('0.0001')


def _to_decimal(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class LoanBillingService:
    def ensure_schedule(self, loan: LoanApplication, currency: str = 'GHS') -> RepaymentSchedule:
        schedule = get_schedule(loan.loan_id)
        if schedule:
            return schedule
        original_amount = _to_decimal(Decimal(str(loan.requested_amount)))
        schedule = RepaymentSchedule(
            loan_id=loan.loan_id,
            currency=currency,
            original_amount=original_amount,
            outstanding_amount=original_amount,
        )
        return save_schedule(schedule)

    def apply_repayment(
        self,
        loan_id: str,
        amount: Decimal,
        currency: str,
        paid_at: Optional[datetime] = None
    ) -> tuple[RepaymentSchedule, Decimal]:
        schedule = get_schedule(loan_id)
        if not schedule:
            loan = get_application(loan_id)
            if not loan:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='loan not found')
            schedule = self.ensure_schedule(loan, currency)

        if currency != schedule.currency:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='currency mismatch')

        normalized_amount = _to_decimal(amount)
        if normalized_amount <= Decimal('0'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='amount must be positive')

        before_outstanding = schedule.outstanding_amount
        applied = min(before_outstanding, normalized_amount)
        applied = _to_decimal(applied)
        schedule.outstanding_amount = _to_decimal(before_outstanding - applied)
        schedule.paid_amount = _to_decimal(schedule.paid_amount + applied)
        schedule.last_paid_at = paid_at or datetime.utcnow()
        schedule.updated_at = datetime.utcnow()
        schedule.status = 'REPAID' if schedule.outstanding_amount == Decimal('0') else 'ACTIVE'
        save_schedule(schedule)
        return schedule, applied
