from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag

SOURCE_URL = "https://www.cdac.in/index.aspx?id=current_jobs"


@dataclass(frozen=True)
class JobListing:
    title: str
    advertisement_url: str
    source_url: str = SOURCE_URL


def normalize_url(url: str, base_url: str = SOURCE_URL) -> str:
    absolute = urljoin(base_url, url.strip())
    parsed = urlparse(absolute)

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            "",
        )
    )


def is_supporting_document(title: str) -> bool:
    """
    Exclude documents that support a recruitment advertisement
    rather than being recruitment advertisements themselves.
    """
    text = title.lower().strip()

    supporting_phrases = [
        "application form",
        "application format",
        "format for application",
        "interview application",
        "application for interview",
        "syllabus",
        "faq",
        "admit card",
        "intimation card",
    ]

    return any(phrase in text for phrase in supporting_phrases)


def parse_current_openings(
    html: str,
    source_url: str = SOURCE_URL,
) -> list[JobListing]:

    soup = BeautifulSoup(html, "html.parser")

    current_heading = find_heading(soup, "current openings")

    if current_heading is None:
        raise ValueError(
            "Could not find the 'Current Openings' section."
        )

    jobs: list[JobListing] = []

    # Everything after "Current Openings" belongs to this section
    # until the next major C-DAC job-page section begins.
    stopping_headings = {
        "rolling advertisements",
        "notifications",
        "list of shortlisted/selected candidates for various positions advertised",
        "archive",
    }

    for element in current_heading.find_all_next():

        if not isinstance(element, Tag):
            continue

        # Stop when we reach the next major section.
        if element.name in {"h1", "h2", "h3"}:
            heading_text = " ".join(
                element.get_text(" ", strip=True).lower().split()
            )

            if (
                element is not current_heading
                and heading_text in stopping_headings
            ):
                break

        if element.name != "a":
            continue

        title = element.get_text(" ", strip=True)
        href = element.get("href")

        if not title or not href:
            continue

        # Only remove obvious supporting documents.
        # Do NOT use recruitment-title keywords here.
        if is_supporting_document(title):
            continue

        advertisement_url = normalize_url(
            href,
            source_url,
        )

        jobs.append(
            JobListing(
                title=title,
                advertisement_url=advertisement_url,
                source_url=source_url,
            )
        )

    return deduplicate_jobs(jobs)


def find_heading(
    soup: BeautifulSoup,
    heading_text: str,
) -> Tag | None:

    wanted = " ".join(
        heading_text.lower().split()
    )

    for heading in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6"]
    ):
        actual = " ".join(
            heading.get_text(" ", strip=True).lower().split()
        )

        if actual == wanted:
            return heading

    return None


def deduplicate_jobs(
    jobs: list[JobListing],
) -> list[JobListing]:

    seen_urls: set[str] = set()
    unique_jobs: list[JobListing] = []

    for job in jobs:

        if job.advertisement_url in seen_urls:
            continue

        seen_urls.add(job.advertisement_url)
        unique_jobs.append(job)

    return unique_jobs