from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from telegram import Bot


logger = logging.getLogger(__name__)


load_dotenv()


class TelegramNotifier:
    def __init__(self) -> None:

        self.bot_token = os.getenv(
            "TELEGRAM_BOT_TOKEN"
        )

        self.chat_id = os.getenv(
            "TELEGRAM_CHAT_ID"
        )

        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is not configured."
            )

        if not self.chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID is not configured."
            )

        self.bot = Bot(
            token=self.bot_token
        )

    async def send_job_notification(
        self,
        title: str,
        advertisement_url: str,
    ) -> None:

        message = (
            "🚨 NEW C-DAC JOB POSTING\n\n"
            f"📌 {title}\n\n"
            f"🔗 {advertisement_url}\n\n"
            "Source: C-DAC Current Job Opportunities"
        )

        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
        )