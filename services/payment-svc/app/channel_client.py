import random
from .repository import save_disbursement
from .models import Disbursement


def send_to_channel(disb: Disbursement) -> None:
    # Mock: randomly decide success
    success = random.random() > 0.1
    disb.status = 'SUCCESS' if success else 'FAILED'
    disb.failure_reason = None if success else 'CHANNEL_TIMEOUT'
    save_disbursement(disb)
