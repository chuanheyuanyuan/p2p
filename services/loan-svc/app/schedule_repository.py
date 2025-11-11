from typing import Dict, Optional

from .models import RepaymentSchedule

_schedule_store: Dict[str, RepaymentSchedule] = {}


def save_schedule(schedule: RepaymentSchedule) -> RepaymentSchedule:
    _schedule_store[schedule.loan_id] = schedule
    return schedule


def get_schedule(loan_id: str) -> Optional[RepaymentSchedule]:
    return _schedule_store.get(loan_id)
