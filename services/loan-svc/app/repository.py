from typing import Dict, Optional
from datetime import datetime

from .models import LoanApplication

_store: Dict[str, LoanApplication] = {}


def save_application(app: LoanApplication) -> LoanApplication:
    app.updated_at = datetime.utcnow()
    _store[app.loan_id] = app
    return app


def get_application(loan_id: str) -> Optional[LoanApplication]:
    return _store.get(loan_id)
