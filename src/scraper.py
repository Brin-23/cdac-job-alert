from __future__ import annotations

import logging
import time

import requests


SOURCE_URL = "https://www.cdac.in/index.aspx?id=current_jobs"

USER_AGENT = (
    "CDACJobMonitor/1.0 "
    "(read-only recruitment monitor)"
)

logger = logging.getLogger(__name__)


class CDACScraper:
    """Read-only HTTP scraper for the C-DAC Current Job Opportunities page."""

    def __init__(
        self,
        source_url: str = SOURCE_URL,
        timeout: int = 20,
        max_retries: int = 3,
    ) -> None:
        self.source_url = source_url
        self.timeout = timeout
        self.max_retries = max_retries

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
            }
        )

    def fetch_page(self) -> str:
        """
        Download the C-DAC Current Job Opportunities page.

        Retries a small number of times with exponential backoff.
        """

        last_error: Exception | None = None

        for attempt in range(self.max_retries):

            try:
                logger.info(
                    "Requesting C-DAC page "
                    "(attempt %d/%d)",
                    attempt + 1,
                    self.max_retries,
                )

                response = self.session.get(
                    self.source_url,
                    timeout=self.timeout,
                )

                # Don't repeatedly hammer the server if rate-limited.
                if response.status_code == 429:
                    raise requests.HTTPError(
                        "C-DAC returned HTTP 429 "
                        "(Too Many Requests)"
                    )

                # Handle forbidden access gracefully.
                if response.status_code == 403:
                    raise requests.HTTPError(
                        "C-DAC returned HTTP 403 "
                        "(Forbidden)"
                    )

                response.raise_for_status()

                logger.info(
                    "C-DAC page downloaded successfully."
                )

                return response.text

            except requests.RequestException as exc:

                last_error = exc

                logger.warning(
                    "Request failed: %s",
                    exc,
                )

                # Don't retry after the final attempt.
                if attempt == self.max_retries - 1:
                    break

                # 1 second, then 2 seconds, then 4 seconds.
                delay = 2**attempt

                logger.info(
                    "Retrying in %d seconds...",
                    delay,
                )

                time.sleep(delay)

        raise RuntimeError(
            "Unable to fetch the C-DAC Current Job "
            "Opportunities page."
        ) from last_error