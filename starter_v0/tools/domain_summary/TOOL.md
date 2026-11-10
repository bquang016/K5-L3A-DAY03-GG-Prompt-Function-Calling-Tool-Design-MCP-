
---

name: domain_summary
track: core
kind: local_formatter
requires_env: []
inputs: [urls]
outputs: [total_urls, domain_counts]
side_effect: false

---

# domain_summary

Summarizes a list of URLs by domain.

## Purpose

Count how many URLs belong to each domain.

## Inputs

- urls: List of HTTP or HTTPS URL strings.

## Outputs

- total_urls: Total number of valid URLs.
- domain_counts: Dictionary containing domain names and their URL counts.

## Behavior

- Accept HTTP and HTTPS URLs.
- Normalize domain names to lowercase.
- Group URLs belonging to the same domain.
- Return an error dictionary for invalid input.
- Does not make external API requests.
