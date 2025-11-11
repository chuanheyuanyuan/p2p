from typing import Optional, TYPE_CHECKING
from uuid import uuid4
from fastapi import HTTPException, status

from .models import LoanApplication
from .repository import save_application, get_application

if TYPE_CHECKING:
    from .billing_service import LoanBillingService


class LoanService:
    def __init__(self, billing_service: Optional['LoanBillingService'] = None) -> None:
        self.billing_service = billing_service

    def create_draft(self, user_id: str, product_id: str, amount: float, term_days: int) -> LoanApplication:
        loan_id = uuid4().hex
        app = LoanApplication(
            loan_id=loan_id,
            user_id=user_id,
            product_id=product_id,
            requested_amount=amount,
            term_days=term_days
        )
        saved = save_application(app)
        if self.billing_service:
            self.billing_service.ensure_schedule(saved)
        return saved

    def submit(self, loan_id: str) -> LoanApplication:
        app = get_application(loan_id)
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='loan not found')
        if app.status != 'DRAFT':
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='invalid status transition')
        app.status = 'SUBMITTED'
        save_application(app)
        return app
