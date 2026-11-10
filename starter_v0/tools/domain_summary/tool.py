from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def domain_summary(urls: Any) -> dict[str, Any]:
    """Đếm số URL theo từng tên miền."""
    if not isinstance(urls, list) or len(urls) == 0:
        return {
            "tool": "domain_summary",
            "error": "urls phải là một danh sách URL không rỗng",
        }

    counts: dict[str, int] = {}
    invalid: list[Any] = []

    for item in urls:
        if not isinstance(item, str):
            invalid.append(item)
            continue

        url = item.strip()
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            invalid.append(item)
            continue

        domain = parsed.hostname.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        counts[domain] = counts.get(domain, 0) + 1

    if invalid:
        return {
            "tool": "domain_summary",
            "error": "Chứa URL không hợp lệ hoặc phần tử sai kiểu",
            "invalid_urls": [str(x) for x in invalid],
        }

    sorted_counts = dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    return {
        "tool": "domain_summary",
        "total_urls": len(urls),
        "valid_urls": len(urls),
        "domain_counts": sorted_counts,
        "domains": sorted_counts,
    }
