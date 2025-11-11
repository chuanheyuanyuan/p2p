import logging

logger = logging.getLogger(__name__)


class OTPProvider:
    def __init__(self) -> None:
        self.logger = logger

    async def send(self, phone: str, country_code: str, channel: str, code: str) -> None:
        # TODO: integrate with real SMS/WhatsApp provider
        self.logger.info(
            "[OTP] send code=%s via %s to %s%s",
            code,
            channel,
            country_code,
            phone,
        )
