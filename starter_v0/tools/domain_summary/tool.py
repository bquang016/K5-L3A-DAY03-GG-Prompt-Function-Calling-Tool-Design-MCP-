
from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


def domain_summary(urls: list[str] | None = None) -> dict[str, Any]:
    """
    Count valid URLs grouped by domain.
    """

    # 1. Validate input
    if not isinstance(urls, list):
        return {
            "tool": "domain_summary",
            "error": "urls must be a list of strings"
        }

    domain_counts: dict[str, int] = {}

    # 2. Process URLs
    for url in urls:

        # Reject non-string or empty values
        if not isinstance(url, str) or not url.strip():
            return {
                "tool": "domain_summary",
                "error": "Each URL must be a non-empty string"
            }

        try:
            parsed = urlsplit(url.strip())

            # Only accept HTTP and HTTPS
            if parsed.scheme.lower() not in ("http", "https"):
                raise ValueError

            # Extract hostname
            domain = parsed.hostname

            if not domain:
                raise ValueError

            # Normalize domain
            domain = domain.lower()

            # Count domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        except ValueError:
            return {
                "tool": "domain_summary",
                "error": f"Invalid URL: {url}"
            }

    # 3. Return result
    return {
        "tool": "domain_summary",
        "total_urls": sum(domain_counts.values()),
        "domain_counts": domain_counts
    }
