from __future__ import annotations

import asyncio
import logging

from database import JobDatabase
from notifier import TelegramNotifier
from parser import parse_current_openings
from scraper import CDACScraper


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def send_notifications(new_jobs) -> None:
    if not new_jobs:
        return

    notifier = TelegramNotifier()

    for job in new_jobs:
        await notifier.send_job_notification(
            title=job.title,
            advertisement_url=job.advertisement_url,
        )


def main() -> None:

    scraper = CDACScraper()

    logging.info(
        "Fetching C-DAC Current Job Opportunities..."
    )

    html = scraper.fetch_page()

    logging.info(
        "Downloaded %d characters.",
        len(html),
    )

    jobs = parse_current_openings(html)

    logging.info(
        "Found %d current job advertisements.",
        len(jobs),
    )

    database = JobDatabase()

    new_jobs = []

    for job in jobs:

        is_new = database.insert_job(job)

        if is_new:

            new_jobs.append(job)

            logging.info(
                "NEW JOB: %s",
                job.title,
            )

        else:

            database.update_last_seen(
                job.advertisement_url
            )

            logging.info(
                "Already known: %s",
                job.title,
            )

    # Send Telegram notifications only for genuinely new jobs.
    if new_jobs:

        asyncio.run(
            send_notifications(new_jobs)
        )

    print()
    print("=" * 80)
    print("RUN SUMMARY")
    print("=" * 80)

    print(
        f"Current advertisements : {len(jobs)}"
    )

    print(
        f"New advertisements     : {len(new_jobs)}"
    )

    if new_jobs:

        print()
        print("NOTIFICATIONS SENT:")

        for job in new_jobs:

            print()
            print(job.title)
            print(job.advertisement_url)

    else:

        print()
        print("No genuinely new advertisements.")

    print("=" * 80)


if __name__ == "__main__":
    main()