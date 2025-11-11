from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import LoanApplication

CONTRACT_DIR = Path(__file__).resolve().parent.parent / 'contracts'
CONTRACT_DIR.mkdir(exist_ok=True, parents=True)


def generate_contract(loan: LoanApplication) -> dict:
    content = (
        f"Loan ID: {loan.loan_id}\n"
        f"User ID: {loan.user_id}\n"
        f"Product: {loan.product_id}\n"
        f"Amount: {loan.requested_amount}\n"
        f"Term: {loan.term_days} days\n"
        f"Generated at: {datetime.utcnow().isoformat()}\n"
    )
    path = CONTRACT_DIR / f"{loan.loan_id}.txt"
    path.write_text(content, encoding='utf-8')
    expire_at = datetime.utcnow() + timedelta(minutes=15)
    return {
        'loanId': loan.loan_id,
        'contractUrl': str(path),
        'expiresAt': expire_at.isoformat() + 'Z'
    }
