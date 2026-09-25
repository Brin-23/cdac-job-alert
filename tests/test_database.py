from pathlib import Path

from database import JobDatabase
from parser import JobListing


def test_insert_and_duplicate_detection(
    tmp_path: Path,
):

    database_path = tmp_path / "test.sqlite3"

    database = JobDatabase(
        database_path
    )

    job = JobListing(
        title="Project Engineer",
        advertisement_url=(
            "https://www.cdac.in/test-job.pdf"
        ),
    )

    first_insert = database.insert_job(job)

    second_insert = database.insert_job(job)

    assert first_insert is True

    assert second_insert is False


def test_different_jobs_are_stored(
    tmp_path: Path,
):

    database_path = tmp_path / "test.sqlite3"

    database = JobDatabase(
        database_path
    )

    job1 = JobListing(
        title="Project Engineer",
        advertisement_url=(
            "https://www.cdac.in/job1.pdf"
        ),
    )

    job2 = JobListing(
        title="Software Engineer",
        advertisement_url=(
            "https://www.cdac.in/job2.pdf"
        ),
    )

    assert database.insert_job(job1) is True

    assert database.insert_job(job2) is True

    jobs = database.get_all_jobs()

    assert len(jobs) == 2