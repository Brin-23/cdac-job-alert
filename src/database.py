from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from parser import JobListing


DATABASE_PATH = Path("data") / "cdac_jobs.sqlite3"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_content_hash(job: JobListing) -> str:
    content = "|".join(
        [
            job.title.strip(),
            job.advertisement_url.strip(),
            job.source_url.strip(),
        ]
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


class JobDatabase:
    def __init__(
        self,
        database_path: Path = DATABASE_PATH,
    ) -> None:

        self.database_path = database_path

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_tables()

    def _connect(self) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _create_tables(self) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    title TEXT NOT NULL,

                    location TEXT,

                    advertisement_url TEXT NOT NULL,

                    source_url TEXT NOT NULL,

                    publication_date TEXT,

                    deadline TEXT,

                    eligibility_text TEXT,

                    experience_text TEXT,

                    relevance_category TEXT,

                    first_seen_at TEXT NOT NULL,

                    last_seen_at TEXT NOT NULL,

                    content_hash TEXT NOT NULL,

                    UNIQUE(advertisement_url)
                )
                """
            )

            connection.commit()

    def job_exists(
        self,
        advertisement_url: str,
    ) -> bool:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT 1
                FROM jobs
                WHERE advertisement_url = ?
                LIMIT 1
                """,
                (advertisement_url,),
            ).fetchone()

            return row is not None

    def insert_job(
        self,
        job: JobListing,
        *,
        location: str | None = None,
        publication_date: str | None = None,
        deadline: str | None = None,
        eligibility_text: str | None = None,
        experience_text: str | None = None,
        relevance_category: str | None = None,
    ) -> bool:

        now = utc_now()

        content_hash = calculate_content_hash(job)

        with self._connect() as connection:

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO jobs (
                    title,
                    location,
                    advertisement_url,
                    source_url,
                    publication_date,
                    deadline,
                    eligibility_text,
                    experience_text,
                    relevance_category,
                    first_seen_at,
                    last_seen_at,
                    content_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.title,
                    location,
                    job.advertisement_url,
                    job.source_url,
                    publication_date,
                    deadline,
                    eligibility_text,
                    experience_text,
                    relevance_category,
                    now,
                    now,
                    content_hash,
                ),
            )

            connection.commit()

            return cursor.rowcount == 1

    def update_last_seen(
        self,
        advertisement_url: str,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE jobs
                SET last_seen_at = ?
                WHERE advertisement_url = ?
                """,
                (
                    utc_now(),
                    advertisement_url,
                ),
            )

            connection.commit()

    def get_all_jobs(self) -> list[sqlite3.Row]:

        with self._connect() as connection:

            return connection.execute(
                """
                SELECT *
                FROM jobs
                ORDER BY first_seen_at DESC
                """
            ).fetchall()