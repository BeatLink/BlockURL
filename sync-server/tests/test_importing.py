from blockurl.importing import parse_urls


def test_plain_list_one_url_per_line():
    text = "https://a.com/1\nhttps://b.com/2\n"
    assert parse_urls(text) == ["https://a.com/1", "https://b.com/2"]


def test_blank_lines_and_whitespace_are_dropped():
    text = "  https://a.com/1  \n\n\nhttps://b.com/2\n   \n"
    assert parse_urls(text) == ["https://a.com/1", "https://b.com/2"]


def test_byte_order_mark_is_stripped():
    assert parse_urls("﻿https://a.com/1\n") == ["https://a.com/1"]


def test_empty_file_returns_nothing():
    assert parse_urls("") == []
    assert parse_urls("\n  \n") == []
    assert parse_urls(None) == []


def test_csv_header_names_the_url_column():
    text = "name,url,added\nExample,https://a.com/1,2026-01-01\nOther,https://b.com/2,2026-01-02\n"
    assert parse_urls(text) == ["https://a.com/1", "https://b.com/2"]


def test_csv_header_row_is_not_imported_as_a_url():
    text = "url\nhttps://a.com/1\n"
    assert parse_urls(text) == ["https://a.com/1"]


def test_csv_without_a_header_uses_the_column_holding_urls():
    text = "Example,https://a.com/1,2026-01-01\nOther,https://b.com/2,2026-01-02\n"
    assert parse_urls(text) == ["https://a.com/1", "https://b.com/2"]


def test_semicolon_and_tab_delimiters():
    assert parse_urls("name;url\nExample;https://a.com/1\n") == ["https://a.com/1"]
    assert parse_urls("name\turl\nExample\thttps://a.com/1\n") == ["https://a.com/1"]


def test_quoted_fields_keep_their_commas():
    text = 'url,note\nhttps://a.com/1,"first, second"\n'
    assert parse_urls(text) == ["https://a.com/1"]


def test_domain_only_rows_are_recognised():
    text = "domain,count\nexample.com,4\nother.org,2\n"
    assert parse_urls(text) == ["example.com", "other.org"]


def test_rows_missing_the_url_column_are_skipped():
    text = "name,url\nExample,https://a.com/1\nIncomplete\nOther,https://b.com/2\n"
    assert parse_urls(text) == ["https://a.com/1", "https://b.com/2"]


def test_numbers_and_dates_are_not_mistaken_for_urls():
    text = "1.5,https://a.com/1,2026-01-01\n2.5,https://b.com/2,2026-01-02\n"
    assert parse_urls(text) == ["https://a.com/1", "https://b.com/2"]


def test_file_with_no_urls_at_all_keeps_every_row_and_takes_the_first_column():
    text = "alpha,beta\ngamma,delta\n"
    assert parse_urls(text) == ["alpha", "gamma"]


def test_one_column_file_keeps_a_first_line_that_is_not_a_header_name():
    text = "example.com\nother.org\n"
    assert parse_urls(text) == ["example.com", "other.org"]
