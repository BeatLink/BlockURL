"""Reads the URLs out of an uploaded file, whether it is a plain list or a CSV.

A plain list is one URL per line. A CSV may carry a header row and several
columns, so the URL column is picked by its header name, or by which column
holds the most URLs when the file has no header.
"""

import csv

URL_HEADERS = {"url", "urls", "link", "links", "address", "site", "website", "domain", "host", "hostname"}

DELIMITERS = ",;\t|"

SAMPLE_LINES = 20


def parse_urls(text):
    """Return the URLs in an uploaded file, taking the URL column when it is a CSV."""
    rows = _read_rows(text)
    if not rows:
        return []
    header, body = _split_header(rows)
    if max(len(row) for row in rows) == 1:
        return [cell.strip() for row in body for cell in row if cell.strip()]
    column = _choose_column(header, body)
    return [row[column].strip() for row in body if len(row) > column and row[column].strip()]


def _read_rows(text):
    """Split the text into rows, guessing which character separates the columns."""
    lines = [line for line in (text or "").lstrip("﻿").splitlines() if line.strip()]
    if not lines:
        return []
    try:
        delimiter = csv.Sniffer().sniff("\n".join(lines[:SAMPLE_LINES]), delimiters=DELIMITERS).delimiter
    except csv.Error:
        delimiter = ","
    return [row for row in csv.reader(lines, delimiter=delimiter) if any(cell.strip() for cell in row)]


def _split_header(rows):
    """Return the header row and the rows below it, or no header when the first row is already data."""
    first, rest = rows[0], rows[1:]
    if any(cell.strip().lower() in URL_HEADERS for cell in first):
        return first, rest
    # A first row without a URL only reads as a header when the rows below do hold URLs.
    if not any(_looks_like_url(cell) for cell in first) and _holds_a_url(rest):
        return first, rest
    return None, rows


def _holds_a_url(rows):
    """Return whether any cell in these rows reads as a web address."""
    return any(_looks_like_url(cell) for row in rows for cell in row)


def _choose_column(header, body):
    """Return the index of the column holding the URLs."""
    if header:
        for index, cell in enumerate(header):
            if cell.strip().lower() in URL_HEADERS:
                return index
    if not body:
        return 0
    width = max(len(row) for row in body)
    scores = [sum(_looks_like_url(row[index]) for row in body if len(row) > index) for index in range(width)]
    best = max(range(width), key=lambda index: scores[index])
    return best if scores[best] else 0


def _looks_like_url(value):
    """Return whether a cell reads as a web address rather than a name, date or number."""
    value = value.strip()
    if not value or any(character.isspace() for character in value):
        return False
    if value.lower().startswith(("http://", "https://")):
        return True
    host = value.split("/", 1)[0]
    if "." not in host:
        return False
    suffix = host.rsplit(".", 1)[1]
    return len(suffix) >= 2 and suffix.isalpha()
