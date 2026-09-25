import asyncio

from notifier import TelegramNotifier


async def main() -> None:

    notifier = TelegramNotifier()

    await notifier.send_job_notification(
        title="TEST — C-DAC Job Monitor",
        advertisement_url=(
            "https://www.cdac.in/index.aspx?id=current_jobs"
        ),
    )

    print("Telegram test notification sent.")


if __name__ == "__main__":
    asyncio.run(main())