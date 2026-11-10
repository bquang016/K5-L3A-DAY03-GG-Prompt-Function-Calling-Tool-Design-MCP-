from urllib.parse import urlparse


def domain_summary(urls: list) -> dict:
    """Đếm số URL theo từng tên miền."""
    # 1. Kiểm tra đầu vào: phải là list và không rỗng
    if not isinstance(urls, list) or len(urls) == 0:
        return {"error": "urls phải là một danh sách URL không rỗng"}

    counts = {}
    invalid = []

    for item in urls:
        # 2. Phần tử không phải chuỗi -> coi là URL lỗi
        if not isinstance(item, str):
            invalid.append(str(item))
            continue

        url = item.strip()
        parsed = urlparse(url)

        # 3. URL hợp lệ phải có http/https và có tên miền
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            invalid.append(item)
            continue

        domain = parsed.hostname.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        counts[domain] = counts.get(domain, 0) + 1

    # 4. Nếu không có URL nào hợp lệ -> trả lỗi
    if not counts:
        return {"error": "Không có URL hợp lệ nào", "invalid_urls": invalid}

    # Sắp xếp domain có nhiều URL nhất lên đầu
    sorted_counts = dict(sorted(counts.items(), key=lambda kv: -kv[1]))
    return {
        "total_urls": len(urls),
        "valid_urls": sum(counts.values()),
        "invalid_urls": invalid,
        "domains": sorted_counts,
    }